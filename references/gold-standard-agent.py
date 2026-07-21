"""Reference implementation: an expert-grade LangChain v1 agent.

!! ILLUSTRATIVE — DOES NOT RUN AS-IS. `warehouse`, `mailer`, `preference_store`
!! and `WarehouseTimeout` are stand-ins for your own infrastructure. Middleware
!! constructor signatures were verified against langchain v1 (langchain_v1) at
!! time of writing; VERIFY AGAINST YOUR INSTALLED VERSION before asserting any
!! of them in a review (see SKILL.md "Verify before asserting").
!!
!! SHAPE: this is the `create_agent` shape. Most real apps met in the wild are
!! LangGraph-native (StateGraph + custom nodes), where the same intents appear
!! as config ceilings, `.with_retry()` on model bindings, a dedicated
!! compression node, and a homegrown call wrapper enforcing a message contract.
!! Judge those by intent satisfied, never by middleware imported.

Annotated with [#N] markers pointing at the numbered practices in SKILL.md.
This is a *shape* to compare against, not a template to copy verbatim —
a one-shot script legitimately skips persistence and HITL.

Scenario: an internal analytics agent that answers questions about revenue by
querying a warehouse and optionally emailing a report to a stakeholder.
Consequential action (email) + multi-turn + production = the full stack.
"""

from __future__ import annotations

import logging
import os
from typing import Literal

from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelCallLimitMiddleware,
    ModelFallbackMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
    ToolCallLimitMiddleware,
)
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.postgres import PostgresSaver
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)  # [#18] module logger, no print()

# [#5] Model identity is configuration, never a hardcoded provider class.
#      Swapping providers is an env change, not a code change.
PRIMARY_MODEL = os.environ["ANALYTICS_AGENT_MODEL"]  # e.g. "anthropic:claude-sonnet-4-6"
FALLBACK_MODEL = os.environ["ANALYTICS_AGENT_FALLBACK_MODEL"]


# ---------------------------------------------------------------------------
# Output contract
# ---------------------------------------------------------------------------

# [#10] The agent's answer is a typed object, not prose to be parsed downstream.
class RevenueAnswer(BaseModel):
    """Structured result of a revenue question."""

    headline: str = Field(description="One-sentence answer to the user's question.")
    figure_usd: float | None = Field(
        default=None, description="Primary figure in USD, if the question had one."
    )
    period: str = Field(description="Time period the figure covers, e.g. '2026-Q1'.")
    confidence: Literal["high", "medium", "low"]
    caveats: list[str] = Field(
        default_factory=list, description="Data quality or interpretation caveats."
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

# [#11] Small, single-purpose, fully typed. The docstring is prompt engineering:
#       it is the specification the model reads to decide when and how to call.
@tool
def query_revenue(
    metric: Literal["gross", "net", "arr"],
    start_date: str,
    end_date: str,
    region: str | None = None,
) -> str:
    """Query the revenue warehouse for a single metric over a date range.

    Use for factual revenue figures. Dates must be ISO format (YYYY-MM-DD).
    Omit `region` for a global figure. Returns a compact summary, not raw rows.

    Args:
        metric: Which revenue measure to return.
        start_date: Inclusive start of the period, ISO format.
        end_date: Inclusive end of the period, ISO format.
        region: Optional ISO country code to filter by.
    """
    try:
        rows = warehouse.run(metric, start_date, end_date, region)  # noqa: F821
    except WarehouseTimeout as exc:  # noqa: F821
        # [#12] Recoverable failures are returned to the model as information it
        #       can act on (retry narrower, try another period) — not raised.
        logger.debug("warehouse timeout: %s", exc)
        return (
            "Query timed out. The range may be too wide — retry with a shorter "
            "period or a single region."
        )

    if not rows:
        return f"No {metric} revenue rows found for {start_date}..{end_date}."

    # [#9] Tool output is summarized before entering context. Never dump 10k rows
    #      into the message history.
    return summarize_rows(rows, limit=20)  # noqa: F821


@tool
def send_report(recipient_email: str, subject: str, body_markdown: str) -> str:
    """Email a finished revenue report to an internal stakeholder.

    Only send after the user has confirmed the content. Recipient must be an
    internal address.

    Args:
        recipient_email: Internal recipient address.
        subject: Email subject line.
        body_markdown: Report body in Markdown.
    """
    if not recipient_email.endswith("@example-corp.com"):
        # [#12] Invariant violation, not a recoverable condition -> raise.
        #       (Guard with an explicit raise, never `assert`. [#18])
        raise ValueError("send_report may only target internal addresses")

    message_id = mailer.send(recipient_email, subject, body_markdown)  # noqa: F821
    return f"Sent. Message id: {message_id}"


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an internal revenue analyst.

Answer with figures pulled from the warehouse — never estimate from memory.
State the period every figure covers. If the data is partial or the question is
ambiguous, say so in `caveats` and lower your confidence rather than guessing.
Never email a report before the user has approved its content.
"""


def build_agent(checkpointer: PostgresSaver):
    """Construct the analytics agent.

    [#1] No hand-rolled loop. [#4] One factory call that reads as a policy:
    what model, what it can do, what it returns, what constrains it, where
    state lives. A security reviewer can audit this function alone.
    """
    model = init_chat_model(PRIMARY_MODEL)

    return create_agent(
        model,
        tools=[query_revenue, send_report],
        system_prompt=SYSTEM_PROMPT,
        response_format=RevenueAnswer,  # [#10]
        # [#17] ORDER IS SEMANTICALLY LOAD-BEARING. Hooks compose onion-style:
        #       `before_model` runs in list order, `after_model` in reverse, so
        #       earlier entries are "outer". Order decides what each middleware
        #       sees — e.g. summarization placed before redaction would summarize
        #       un-redacted text. It does NOT govern what tracing captures:
        #       tracers are callbacks on the model/tool call, not middleware.
        #       Keeping raw PII out of traces is `apply_to_*` flags plus tracer
        #       config, never ordering alone.
        middleware=[
            # Outermost: hard spend ceilings. Nothing below can loop forever. [#16]
            ModelCallLimitMiddleware(thread_limit=40, run_limit=25),
            ToolCallLimitMiddleware(thread_limit=60, run_limit=30),
            # [#17] PII. NOTE THE NON-DEFAULT FLAGS — this is the single most
            # common security mistake with this middleware. Defaults are
            # apply_to_input=True, apply_to_output=False, apply_to_tool_results=False,
            # so a bare `PIIMiddleware("email")` inspects USER MESSAGES ONLY and
            # would miss customer emails arriving in warehouse query results —
            # which is precisely the exposure in this agent.
            PIIMiddleware(
                "email",
                strategy="redact",
                apply_to_input=True,
                apply_to_output=True,
                apply_to_tool_results=True,
            ),
            # `block` raises PIIDetectionError and ends the run — chosen here
            # because a card number in an analytics agent is never legitimate.
            PIIMiddleware("credit_card", strategy="block", apply_to_tool_results=True),
            # Provider outage handling is declarative, not try/except. [#7]
            ModelFallbackMiddleware(FALLBACK_MODEL),
            # Context budget expressed as a fraction of *this* model's window,
            # so it stays correct when PRIMARY_MODEL changes. [#6][#8]
            SummarizationMiddleware(
                model=model,
                trigger=("fraction", 0.8),
                keep=("messages", 20),
            ),
            # Innermost: the approval gate wraps the action it guards. [#14]
            HumanInTheLoopMiddleware(interrupt_on={"send_report": True}),
        ],
        # [#13] Durable, resumable state. Also the precondition that makes the
        #       interrupt-based approval gate above work at all. [#14]
        checkpointer=checkpointer,
        # [#15] Cross-thread memory (stakeholder preferences, saved definitions)
        #       lives in a store, not smuggled into the message history.
        store=preference_store,  # noqa: F821
    )


# ---------------------------------------------------------------------------
# Invocation
# ---------------------------------------------------------------------------

def answer(agent, question: str, thread_id: str) -> RevenueAnswer:
    """Run one turn. [#13] thread_id is explicit and stable per conversation."""
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    # [#10] Typed straight out. No json.loads, no regex, no string surgery.
    return result["structured_response"]


# ---------------------------------------------------------------------------
# What good tests look like  [#19]
# ---------------------------------------------------------------------------
#
# def test_refuses_external_recipient():
#     model = GenericFakeChatModel(messages=iter([...]))   # deterministic, no network
#     agent = create_agent(model, tools=[send_report], ...)
#     ...
#     # Assert on TRAJECTORY (which tools ran, in what order, final typed output),
#     # never on exact prose:
#     assert [c["name"] for c in calls] == ["query_revenue"]
#     assert result.confidence == "low"
#
# Live-API calls in unit tests are a finding, not a style preference.
# If this module shipped a custom chat model or vectorstore, it would also run
# the `langchain-tests` standard conformance suite.
#
# [#20] Tracing is configured via env (LANGSMITH_TRACING / OTel exporter) at the
#       process edge — not with print statements sprinkled through tools — and a
#       graded eval set gates prompt/model changes before they ship.
#
# [#2] If this agent later needs branching control flow, multiple specialized
#      agents, or a planning phase, the move is DOWN to a LangGraph StateGraph
#      (create_agent already returns a CompiledStateGraph) or UP to deepagents —
#      not monkey-patching this factory.
