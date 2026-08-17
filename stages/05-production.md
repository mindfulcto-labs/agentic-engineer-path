# Stage 05: Production

Running agent systems is an operations discipline. Most of what you know from running ordinary services still applies. This stage covers what is different.

## Observability: the trace is the unit of truth

For a normal service you reason from logs and metrics. For an agent you reason from traces, because the interesting question is rarely "did the request fail" and usually "why did the agent decide that". A trace captures the full trajectory: each model call with its input context, each tool call with arguments and results, each retry, and the token counts and latency at every step.

Instrument from day one. Retrofitting tracing onto an agent system is miserable, because the interesting state lives in the assembled context, and if you did not record it at the time it is gone. Use OpenTelemetry conventions where you can and an LLM-aware layer such as Langfuse on top, so traces link to eval scores and cost. When an agent misbehaves, the workflow is: pull the trace, read the context the model actually saw, and nine times out of ten the mystery dissolves. Without the trace you are guessing, and guessing about a probabilistic system is a slow way to be wrong.

Two metrics matter beyond standard service health: task success rate, measured by your evals against production traffic samples, and human intervention rate, meaning how often a person had to take over. A falling success rate with a stable error rate is the signature agent failure: every HTTP call succeeded and the outcomes still got worse. Your dashboards must be able to see it.

## Cost control

Token spend is the utility bill of agent systems, and it scales with usage, loop depth, and context size all at once. Uncontrolled, it will surprise you at the end of the month. The controls, in the order I apply them:

1. **Budgets per run**, from stage 04. A hard ceiling per task, enforced in code, with stop-and-escalate behaviour.
2. **Attribution.** Tag every model call with agent, feature, and team. Untagged spend is unmanageable spend, and the first month of tagging always finds one workflow quietly eating half the bill.
3. **Model tiering.** Route easy steps to cheap models and hard steps to strong ones. Classification, extraction, and routing rarely need a frontier model. A gateway layer makes this a config change instead of a code change.
4. **Context discipline.** Cost grows with input tokens, and input tokens grow with lazy context assembly. Summarise old turns, trim tool results, retrieve less and better. Stage 01 habits pay the bill here.
5. **Caching.** Prompt caching for stable system prompts and tool definitions, response caching where inputs genuinely repeat.

## Reliability

Everything you know about distributed systems reliability applies, plus one new dimension: the model itself is a dependency with variable latency, rate limits, outages, and occasional silent behaviour changes.

- **Fallbacks across providers.** A gateway that can route to a second provider turns a model outage into a degradation. Test the fallback path monthly, because an untested fallback is a rumour.
- **Timeouts and retries at every step.** Model calls and tool calls both. Retries on model calls need care, since you pay for every attempt.
- **Checkpointing for long workflows.** A workflow that dies at step nine of ten should resume at step nine. LangGraph-style persistent state earns its keep here.
- **Graceful degradation.** Decide per feature what happens when the agent is unavailable: a queue, a simpler non-agent path, or an honest error. Deciding at design time is cheap. Deciding during the outage is expensive.
- **Pin and stage model versions.** Treat a model upgrade like a dependency upgrade: run it through evals, canary it, keep a rollback. Never let a provider default move you to a new model silently.

## Incident response for agent systems

Agent incidents have a property ordinary incidents lack: the system may have done something wrong while working exactly as built. A misleading answer to a customer, a runaway loop that spent real money, or an action that should have waited for approval are all incidents even though every component was green.

What changes in practice:

- **Declare on outcomes as well as infrastructure.** Define agent-specific incident triggers: intervention rate spike, eval score drop on the production sample, budget breaches, any tier 3 action without its approval record.
- **First move is containment.** Use the kill switch from stage 04, or degrade to the non-agent path. With an agent still acting, diagnosis can wait the thirty seconds pausing takes.
- **Investigate from the trace.** The postmortem question is "what context led to this decision", answered from the audit trail. If the trail cannot answer it, that gap is itself a finding, and fixing it goes on the action list.
- **Feed every incident into the eval set.** The case that bit you becomes a permanent regression test. This loop, incident to eval to release gate, is the most valuable habit in running agents, and teams that keep it stop repeating their failures.

Run game days. Inject a failing tool, a poisoned document, a provider outage, and watch what the on-call engineer can actually see and do. The first game day is always humbling, which is precisely the point of holding it before production traffic arrives.

## Read

- [OpenTelemetry documentation](https://opentelemetry.io/docs/). The tracing substrate. Read the traces concept page if it is new to you.
- [Langfuse documentation](https://langfuse.com/docs). LLM-aware tracing, cost tracking, and eval integration in one place.
- [Site Reliability Engineering (the SRE book)](https://sre.google/sre-book/table-of-contents/). The chapters on SLOs, monitoring, and postmortems transfer directly.
- [The Site Reliability Workbook](https://sre.google/workbook/table-of-contents/). The practical companion, strongest on alerting and incident process.
- [MLflow documentation](https://mlflow.org/docs/latest/). Experiment tracking and model lifecycle, useful once you version prompts and models seriously.
- [OpenAI evals guide](https://platform.openai.com/docs/guides/evals). Running evals against production samples, the mechanism behind outcome-based alerting.
- [What We Learned from a Year of Building with LLMs](https://www.oreilly.com/radar/what-we-learned-from-a-year-of-building-with-llms-part-i/). Practitioners on the operational gap between demo and production. Part one of three, all worth the time.

## Exercises

1. **Instrument your agent.** Take your stage 02 agent and add tracing with Langfuse or OpenTelemetry: every model call with full context, every tool call, token counts, latency, and a cost figure per run. Run ten tasks, then answer from the traces alone: which step is slowest, which is most expensive, and which tool fails most often.
2. **Enforce a budget, then breach it.** Add a per-run cost ceiling to the same agent using your gateway or your own accounting. Give it a task designed to blow the budget. Verify it stops cleanly, reports what it spent, and escalates rather than truncating silently. If you built the llm-gateway route in stage 01, enforce the ceiling there, where it belongs.
3. **Run a one-hour game day.** With a colleague, inject two failures into your instrumented agent: a tool that starts timing out, and a document containing a prompt injection. The colleague, using only your traces and dashboards, must detect both, contain the agent, and write a half-page postmortem with one action item each. Fix what the postmortems find.

## Further reading

Two of my repos collect the wider practice: [aidlc](https://github.com/mindfulcto-labs/aidlc) on running an AI-assisted development lifecycle, and [agentic-harness](https://github.com/mindfulcto-labs/agentic-harness) on harness engineering, meaning the budgets, blast-radius controls, and audit surfaces that wrap production agents.
