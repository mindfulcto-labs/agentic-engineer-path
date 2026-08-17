# Stage 03: Orchestration

You can build one agent. This stage is about systems of agents, and about the honest question that comes first: whether you need more than one at all.

## Single agent first, multi-agent when forced

My default is one agent with good tools. Multi-agent designs cost you coordination overhead, harder debugging, compounded error rates, and token bills that multiply with each participant. Those costs are certain. The benefits are conditional.

The conditions that genuinely justify multiple agents:

- **Context isolation.** The task needs more working material than one context window holds, so sub-agents each take a slice and return summaries. Research over large document sets is the classic case.
- **Separation of privilege.** One agent drafts, a differently-permissioned agent approves. You want the boundary for safety reasons, and a single agent cannot police itself.
- **Genuine parallelism.** Independent subtasks with no shared state, fanned out and joined. If the subtasks are dependent, parallelism is an illusion and a single sequential agent is simpler.

If a proposal for a multi-agent system does not name one of these, it is usually an org chart cosplaying as an architecture. Push back.

## Choosing a framework by workload shape

Frameworks are not interchangeable. Each one encodes a workload shape, and fighting the shape is worse than using no framework.

- **[LangGraph](https://langchain-ai.github.io/langgraph/)** models the workflow as a graph with explicit state, conditional edges, and checkpoints. Choose it for stateful, multi-step workflows where you need strict control over what happens after what, and the ability to persist and resume. This is my default for production workflows that must be auditable.
- **[AutoGen](https://microsoft.github.io/autogen/)** models the workflow as a conversation between agents, with first-class human-in-the-loop support. Choose it for iterative analytical work where a person reviews and redirects between steps.
- **[CrewAI](https://docs.crewai.com/)** models the workflow as a team of role-defined agents handing off tasks. Choose it for pipeline-shaped work that decomposes naturally into roles, such as research then draft then review.
- **[LlamaIndex](https://docs.llamaindex.ai/)** centres on retrieval. Choose it when the hard part of your problem is getting the right knowledge in front of the model, and the agent behaviour is comparatively simple.

One warning from experience: teams pick a framework before they understand their workload, then spend months working around it. Write the workflow as plain code first, even crudely. The shape you discover tells you which framework fits, and sometimes it tells you that 200 lines of your own code is the right answer.

## MCP as the integration surface

The Model Context Protocol (MCP) is an open standard for connecting agents to tools and data. A tool provider implements an MCP server once. Any MCP-capable agent or application can then use it, regardless of which model or framework sits behind the agent.

The practical effect on a platform team is large. Before a standard, every agent-to-system integration was bespoke: N agents times M systems. With MCP you build M servers and every agent gets all of them. Tool definitions, authentication, and transport are specified, so the integration surface becomes a reviewable, versionable artefact rather than glue code scattered through agent repos.

Treat MCP servers the way you treat internal APIs: owned, documented, access-controlled, and tested independently of any agent that consumes them. An MCP server is also a security boundary, since whatever it exposes, every connected agent can attempt. Scope them narrowly. Stage 04 picks this up.

## Read and watch

- [LangGraph documentation](https://langchain-ai.github.io/langgraph/). Read the concepts section on graphs, state, and checkpoints.
- [AutoGen documentation](https://microsoft.github.io/autogen/). Focus on the conversation patterns and human-in-the-loop sections.
- [CrewAI documentation](https://docs.crewai.com/). The core concepts on agents, tasks, and crews are enough to see the shape.
- [LlamaIndex documentation](https://docs.llamaindex.ai/). Read the agents section with retrieval in mind.
- [Model Context Protocol](https://modelcontextprotocol.io/). The specification and quickstart. Build one server before forming an opinion.
- [Introducing the Model Context Protocol, Anthropic](https://www.anthropic.com/news/model-context-protocol). The design intent, useful context for why the protocol looks the way it does.
- [How we built our multi-agent research system, Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system). An honest engineering account of a real multi-agent system, including costs and failure modes. The best available antidote to multi-agent hype.

## Exercises

1. **Same workflow, two shapes.** Take a three-step workflow: fetch data from two sources, reconcile them, produce a report. Build it twice: once as your single agent loop from stage 02 with three tools, once in LangGraph with explicit state and a conditional retry edge. Write a half page comparing debuggability, token cost, and how each handles a mid-run failure. Keep the version you would defend in a design review.
2. **Schema-validate an agent config with confighub.** Clone [confighub](https://github.com/mindfulcto-labs/confighub) and run it locally, following its README. Define a schema for an agent configuration: model, temperature, tool allowlist, iteration cap, budget. Validate a correct config and three broken ones. Config validation is the cheapest orchestration control you will ever deploy, and this exercise shows why.
3. **Expose a tool over MCP.** Take one tool from your stage 02 agent and wrap it as a minimal MCP server using the quickstart at [modelcontextprotocol.io](https://modelcontextprotocol.io/). Connect an MCP-capable client to it. Note what the protocol forced you to make explicit that your in-process tool left implicit.
