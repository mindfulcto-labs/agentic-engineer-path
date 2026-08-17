# Stage 01: Foundations

What an engineer needs to know about LLM behaviour before building anything on top of one. Skip this stage and every later stage gets harder, because you will keep debugging systems whose core component you do not understand.

## The model is a text predictor with a budget

An LLM predicts the next token. A token is a chunk of text, usually three to four characters of English. Everything else follows from this.

The model has a context window: a fixed budget of tokens it can see at once. Your system prompt, the conversation history, retrieved documents, tool definitions, and tool results all spend from the same budget. When the budget runs out, something has to be dropped or summarised, and the model behaves as if the dropped text never existed. Most "the agent forgot" bugs are context budget bugs.

Tokens also cost money and time. Input tokens and output tokens are priced differently, and output tokens are slower because the model produces them one at a time. When someone asks why a request took eleven seconds, count the output tokens before you blame the network.

Temperature controls how the model samples the next token. Low temperature makes output more repeatable. It does not make the model correct, and it does not make it deterministic. Even at temperature zero you can see different outputs across runs on some providers. Design for that.

## Structured outputs are the engineering interface

Free text is fine for chat. It is a poor interface for software. When your code needs to act on model output, ask for structure: JSON matching a schema, an enum, a function call. Modern APIs support this directly, and it turns "parse whatever came back" into "validate against a schema".

My rule: any model output that another program consumes must be schema-validated, and validation failure must be handled as a normal, expected event. Retry with the error message included, fall back, or fail closed. Never assume the model followed the schema because you asked nicely.

## Failure modes you will actually see

These are the failures that show up in production, in rough order of frequency:

1. **Confabulation.** The model states something false with full confidence: an API that does not exist, a file it never read, a number it invented. It is not lying. It is completing text plausibly. Ground it with retrieved facts and verify claims that matter.
2. **Instruction drift.** Over a long context the model slowly stops following early instructions. Repeat critical constraints near the end of the prompt, or restate them each turn.
3. **Format breakage.** The JSON is almost valid. A trailing comma, a comment, markdown fences around the payload. Schema validation plus one retry fixes most of it.
4. **Sycophancy.** The model agrees with a wrong premise in your prompt instead of correcting it. Ask neutral questions when you want honest answers.
5. **Prompt injection.** Text the model reads can steer the model. Any untrusted input, including a web page or a tool result, is a potential instruction channel. Stage 04 covers the defences. For now, remember that data and instructions share one channel.

## Prompt and context engineering are real engineering

A prompt is configuration for a probabilistic component. Treat it like code: version it, review it, test it against known cases. Small edits change behaviour, so no drive-by prompt tweaks in production.

Context engineering is the wider discipline: deciding what goes into the window, in what order, at what level of detail. This matters more than clever wording. A short prompt with the right three documents beats a long prompt with ten irrelevant ones. When behaviour is odd, print the full assembled context and read it top to bottom. The bug is usually visible.

## Read and watch

- [Intro to Large Language Models, Andrej Karpathy](https://www.youtube.com/watch?v=zjkBMFhNj_g). One hour. The best single explanation of what these models are.
- [Deep Dive into LLMs like ChatGPT, Andrej Karpathy](https://www.youtube.com/watch?v=7xTGNNLPyMI). Longer and more technical. Watch after the intro.
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762). The transformer paper. Read the abstract and the architecture section. You do not need the maths to build agents, but you should know the shape of the thing.
- [Hugging Face LLM course, chapter 1](https://huggingface.co/learn/llm-course/chapter1/1). Free, practical, good on tokenisation.
- [tiktoken](https://github.com/openai/tiktoken). A tokeniser you can run locally. Ten minutes with it will teach you more about tokens than any article.
- [Anthropic prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview). Vendor docs, and still the clearest practical guide.
- [Effective context engineering for AI agents, Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). The context budget mindset, from a team that runs agents at scale.
- [OpenAI structured outputs guide](https://platform.openai.com/docs/guides/structured-outputs). How to get schema-conforming JSON out of a model.

## Exercises

1. **Count tokens by hand, then by tool.** Take a 500 word document. Estimate its token count. Check with tiktoken. Then tokenise some code, some JSON, and some non-English text, and note how the ratios differ. Write three sentences on what this means for your context budget.
2. **Break a schema, then survive it.** Write a small script that asks a model for JSON matching a schema with three fields. Validate the response. Deliberately provoke failures with an awkward prompt, then implement one retry that feeds the validation error back to the model. Measure how often the retry rescues the response.
3. **Run llm-gateway offline and add a route.** Clone [llm-gateway](https://github.com/mindfulcto-labs/llm-gateway) and run it locally against a mock provider, following its README. Then add a new route for a second model. This shows you where temperature, token limits, and provider differences live in a real system, at the layer where a platform team actually controls them.
