# Stage 04: Governance

Governance is the stage most engineers want to skip, and the stage that decides whether your agents are allowed to exist in a serious organisation. I have spent a large part of my career on this boundary. The teams that treat governance as engineering ship agents to production. The teams that treat it as paperwork ship demos.

## Permissions and purpose

Every agent should have a written purpose: one paragraph stating what it is for, who it acts for, and what it must never do. This sounds bureaucratic. It is the opposite. A clear purpose statement is what lets you say no quickly when someone asks the agent to do something adjacent, and it is the anchor for every technical control that follows.

From the purpose, derive permissions, and grant them the way you grant production database access: least privilege, explicit, auditable, revocable. Concretely that means a tool allowlist per agent rather than a shared tool pool, read-only credentials unless writing is the purpose, scoped API tokens rather than service-wide ones, and separate identities per agent so audit logs can tell them apart. An agent should authenticate as itself, never as a person, and never as a wildcard service account.

Remember the lesson from stage 01: any text an agent reads can steer it. Prompt injection means an agent's effective permissions are available to whoever can get text in front of it. That web page, that email, that ticket description are all inputs. Set permissions assuming the agent will one day be steered by an attacker, because that is the realistic threat model.

## Risk tiers, budgets, and approval gates

Not every agent needs the same controls, and pretending otherwise guarantees the controls get ignored. Tier by blast radius:

- **Tier 1: reads and drafts.** Summarises, searches, proposes. A human acts on everything. Controls: logging and evals.
- **Tier 2: acts on internal systems, reversibly.** Files tickets, updates configs behind review, runs runbooks in staging. Controls: everything in tier 1, plus budgets and approval gates on defined actions.
- **Tier 3: acts externally or irreversibly.** Customer-facing communication, payments, production changes, deletions. Controls: everything in tier 2, plus human approval on every irreversible action and a documented kill switch that someone on call knows how to use.

Budgets make autonomy bounded instead of open-ended: a spend ceiling per run, an iteration cap, a tool-call limit, a wall-clock timeout. When a budget is hit the agent stops and escalates. It never silently gets more.

Approval gates are checkpoints where a human confirms before the agent proceeds. Place them at irreversibility, at external visibility, and at spend above a threshold. Design the approval experience properly: show the human what will happen, what it costs, and what the rollback is. An approval screen nobody can understand becomes a rubber stamp within a fortnight, and then you have the risk without the control.

## Audit trails and evals as release gates

An audit trail answers, for any action, five questions: which agent, on whose behalf, with what input context, through which tool calls, with what result. Store it structured, append-only, and long enough to satisfy your regulator. When something goes wrong, the difference between a bad day and a very bad day is whether you can replay exactly what the agent saw and did. Build the trail before the incident.

Evals are the release gate that makes change safe. A curated set of cases with expected properties runs on every prompt change, model upgrade, and tool change, exactly like a test suite. No pass, no ship, and prompt edits get no exemption because a prompt edit is a behaviour change. Track scores over time, because silent model updates are real and regression without a code change is normal in this field. Seed the eval set from real failures: every production incident becomes a case.

## The legal floor: UK GDPR and the EU AI Act

You do not need to be a lawyer. You need to know when to call one, and you need to stop believing the comfortable myth that this is someone else's job. Engineers make the design decisions these laws regulate.

**UK GDPR** applies whenever an agent touches personal data, and retrieval-heavy agents touch far more of it than teams expect. The points that bite engineering: you need a lawful basis for processing; data minimisation applies to context windows, so do not stuff a customer's full record into a prompt when three fields serve the purpose; individuals have rights over solely automated decisions with significant effects, which constrains what a tier 3 agent may decide alone; and data sent to a model provider is a transfer to a processor, so know where it goes and under what agreement. The ICO publishes guidance on AI and data protection written for exactly this audience.

**The EU AI Act** classifies AI systems by risk. Prohibited practices are banned outright, high-risk systems carry duties around risk management, data quality, logging, human oversight, and documentation, and general-purpose model providers have their own obligations. If you sell into the EU or your agents affect EU users, classification is not optional. The engineering habit that makes all of it cheaper: the logging, oversight, and documentation duties largely describe the audit trails, approval gates, and eval records this stage already told you to build. Governance done as engineering is compliance nearly for free.

## Read

- [ICO guidance on AI and data protection](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/). The UK regulator, in plain language. Read the fairness and transparency sections first.
- [EU AI Act, full text](https://eur-lex.europa.eu/eli/reg/2024/1689/oj). The regulation itself. Skim the risk categories and Annex III so you can recognise high-risk when you see it.
- [EU AI Act Explorer](https://artificialintelligenceact.eu/). Searchable, readable companion to the text. Use it for lookups.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework). The vocabulary of AI risk management. Useful even outside the US, because auditors speak it.
- [OWASP GenAI Security Project](https://genai.owasp.org/). The Top 10 risks for LLM applications. Prompt injection sits at number one for good reason.
- [Prompt injection series, Simon Willison](https://simonwillison.net/series/prompt-injection/). The clearest sustained thinking on the attack class agents made worse. Read it before you connect an agent to anything with untrusted input.
- [Ragas documentation](https://docs.ragas.io/). Metrics for evaluating retrieval-augmented and agentic pipelines.
- [DeepEval documentation](https://deepeval.com/docs/getting-started). Evals framed as unit tests, which is exactly the right frame for release gates.

## Exercises

1. **Audit a seeded trace with agent-governance-kit.** Clone [agent-governance-kit](https://github.com/mindfulcto-labs/agent-governance-kit) and load one of its seeded traces, following its README. Work through the trace and answer in writing: what was the agent asked to do, what did it actually do, which tool calls exceeded its stated purpose, and at which step should an approval gate have fired. This is the reviewing skill you will use in every incident.
2. **Tier a real agent.** Take the sre-copilot from stage 02 or an agent from your own team. Write its purpose paragraph, assign a risk tier with justification, and specify its budgets, its approval gates, and its kill switch. One page. Have someone senior challenge it.
3. **Build a release gate.** Create an eval set of ten cases for your stage 02 agent using DeepEval or Ragas, including two cases derived from failures you actually observed. Wire the evals into CI so a failing score blocks merge. Then change the prompt in a way that degrades behaviour and confirm the gate catches it.
