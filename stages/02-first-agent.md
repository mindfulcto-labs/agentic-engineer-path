# Stage 02: Your first agent

An agent is an LLM in a loop with tools. That is the whole idea. This stage is about building that loop yourself, once, before any framework hides it from you.

## Tool use, stripped of mystery

The model cannot run code, read files, or call APIs. What it can do is emit a structured request: "call `get_weather` with `city: London`". Your code sees that request, runs the real function, and sends the result back into the context. The model then continues with the result in view.

So a tool is three things: a name, a description the model reads, and a schema for its arguments. The description is an interface contract written in prose, and the model follows it about as well as a rushed colleague follows your API docs. Write tool descriptions with the same care you write public API documentation. Vague descriptions produce wrong calls.

## The agent loop

The loop is short enough to write from memory:

```
context = [system_prompt, user_request]
loop:
    response = model(context, tools)
    if response contains tool calls:
        results = execute(tool_calls)
        context += tool_calls + results
    else:
        return response
```

Everything else in agent engineering is elaboration of this loop: what goes in the context, which tools are offered, when to stop, what to do when a tool fails. Cap the number of iterations. An agent that loops forever calling the same failing tool is the "hello world" of agent bugs, and you will meet it in your first week.

Build this loop yourself in under 150 lines before touching a framework. I insist on this with every new joiner. Engineers who have written the loop can debug any framework, because every framework is this loop wearing a coat.

## Why demos mislead

An agent demo is a single sampled trajectory shown at its best. The same agent, same prompt, run twenty times, will succeed some fraction of those runs. The demo shows you the numerator and hides the denominator.

This has a practical consequence: never evaluate an agent by watching it work once. Evaluate it by running it many times against defined cases and counting. A demo that works is evidence the task is possible. It is no evidence the system is reliable. Most disappointment in this field comes from confusing those two statements.

The gap between demo and production is also wider for agents than for ordinary software, because errors compound across loop iterations. A step that succeeds 95 percent of the time gives you roughly 77 percent over five dependent steps. Long chains need much better per-step reliability than intuition suggests, or checkpoints where a human or a validator can catch drift.

## Testing agent behaviour deterministically

You cannot unit test a model, but you can unit test everything around it, and that is where most bugs live.

- **Fake the model, test the loop.** Record real model responses as fixtures, then replay them. Your loop logic, tool dispatch, retry handling, and stop conditions are ordinary deterministic code. Test them like ordinary code.
- **Test tools in isolation.** Every tool is a function with a schema. Property test the schema validation. Test the failure paths: timeouts, empty results, malformed arguments.
- **Assert on properties of the trajectory.** For end to end tests with a live model, do not assert exact output text. Assert properties: the agent called the search tool before answering, it never called the delete tool, it finished within eight iterations, the final answer contains the order number. Property assertions survive model updates. Exact-match assertions do not.
- **Run flaky tests many times and set a threshold.** "Passes 18 of 20 runs" is a meaningful, monitorable bar. "Passed once on my machine" is not a bar at all.

## Read and watch

- [Building effective agents, Anthropic](https://www.anthropic.com/research/building-effective-agents). The single best short piece on when to use an agent and when a plain workflow is better. Read it twice.
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629). The paper behind the reason-then-act loop pattern.
- [Anthropic tool use documentation](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview). Concrete mechanics of tool definitions and results.
- [OpenAI function calling guide](https://platform.openai.com/docs/guides/function-calling). The same mechanics on the other major API. Knowing both stops you mistaking vendor detail for fundamentals.
- [LLM Powered Autonomous Agents, Lilian Weng](https://lilianweng.github.io/posts/2023-06-23-agent/). A survey of the component ideas: planning, memory, tools.
- [12-factor agents](https://github.com/humanlayer/12-factor-agents). Opinionated production principles. I disagree with parts of it, which is a good reason to read it.
- [Simon Willison on agents](https://simonwillison.net/tags/agents/). Running commentary that stays honest about what works and what does not.

## Exercises

1. **Write the loop.** Build a command line agent in under 150 lines, no framework, with two tools: one that reads a file and one that searches a directory. Give it a task that needs both. Add an iteration cap and log every model request and tool result to a file. Keep this code. Stage 05 instruments it.
2. **Triage an alert with sre-copilot.** Clone [sre-copilot](https://github.com/mindfulcto-labs/sre-copilot) and run it against one of its seeded alerts, following its README. Watch how it gathers context before proposing a diagnosis. Then write a runbook for one failure mode it handles poorly, add it to the runbook set, and re-run the same alert to see whether the behaviour improves.
3. **Prove your agent is testable.** Take your loop from exercise 1. Record the model responses from one successful run as fixtures. Write a replay mode and three deterministic tests: one for correct tool dispatch, one for the iteration cap, one for a tool that throws. The test suite must pass with no network access.
