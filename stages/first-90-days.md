# The first 90 days

This is the schedule I use to bring a new engineer onto an agentic AI team. It maps the five stages onto twelve weeks, with a concrete demo at weeks 1, 2, 4, 8, and 12. The demos are the point. Each one is small, shown to the team, and produces feedback you act on.

Two assumptions. First, you are also doing normal team onboarding: environment setup, codebase tours, meeting people. This plan takes roughly a third of your time in the early weeks and less later. Second, your team has real agent systems you can read and eventually change. If it does not, substitute the reference repos throughout.

## Week 1: foundations and a first call

Work through [stage 01](01-foundations.md), including all three exercises. Get API access sorted on day one, because blocked access is the most common silent onboarding failure. Read your team's system prompts and context assembly code for one production agent, tracing where every token in the window comes from.

**Demo at end of week 1:** your structured-output script from stage 01 exercise 2, shown live: a schema, a model response, a validation failure, and the retry that recovers it. Five minutes. The purpose is to prove your environment works and to get you presenting to the team in your first week.

## Week 2: the loop

Work through [stage 02](02-first-agent.md). Write the agent loop from scratch, then run sre-copilot and do the runbook exercise. Read your team's production agent loop and write down every difference from yours: stop conditions, retry policy, context management. Ask about the differences you cannot explain. Some will be deliberate. Some will be archaeology.

**Demo at end of week 2:** your hand-written agent completing a task live, followed by your deterministic test suite passing with the network off. If the live run misbehaves, better still. Explain from the logs what happened. Recovering from a failed demo in front of the team, using traces, is the most useful thing you can show.

## Weeks 3 and 4: orchestration

Work through [stage 03](03-orchestration.md). Build the same workflow twice, single loop and LangGraph, and form your own view on when the graph earns its complexity. Do the confighub and MCP exercises. Map your team's actual architecture against the stage 03 decision rules: for every multi-agent seam, identify which justification applies, context isolation, privilege separation, or parallelism. Where you cannot find one, ask. You will either learn a constraint you did not see or find a simplification the team wants.

**Demo at end of week 4:** your workflow comparison, presented as a short design review: both implementations, the trace of each handling the same mid-run failure, and your recommendation. Fifteen minutes plus questions. You are practising the judgement this role actually consists of.

## Weeks 5 to 8: governance, and your first real change

Work through [stage 04](04-governance.md) in weeks 5 and 6, including the audit exercise on agent-governance-kit and the eval release gate. Then spend weeks 7 and 8 shipping your first change to a production agent, however small: a tool description fix, an eval case from a real incident, a budget that was missing. Take it through the full path: eval gate, review, staged rollout, trace check after deploy.

Also in this block, write the one-page tier assessment for a production agent your team owns, and have it challenged by the engineer who knows that agent best. Where your assessment disagrees with current controls, one of the two is wrong. Find out which.

**Demo at end of week 8:** your production change and its journey, shown from the audit side: the eval that gated it, the trace before and after, the rollback plan you did not need. If the tier assessment produced a real finding, present that too.

## Weeks 9 to 12: production ownership

Work through [stage 05](05-production.md). Instrument your own agent fully, then join the on-call rotation as a shadow. Sit in on every incident and postmortem in the block, and volunteer to write one postmortem yourself. Run the game day exercise from stage 05 with a teammate as your operator, then swap roles.

In week 11, pick one production cost or reliability improvement your traces suggest, propose it in writing, and ship it if the team agrees: a model tiering change, a context trim, a fallback path, a missing alert.

**Demo at end of week 12:** run the team through a real trace of a real production task, end to end: what the agent saw, what it decided, what it cost, where it could fail, and what would page whom if it did. If you can teach a trace, you can operate the system. This demo is the exit bar for the plan.

## After the 90 days

You should now hold your own view, backed by things you built, on the questions that matter in this field: when an agent beats a workflow, when multi-agent beats single, what a release gate must contain, and what production readiness means for a probabilistic system. From here the path is deeper ownership: take an agent, own its evals, its budget, its incidents, and its roadmap. That is the job.
