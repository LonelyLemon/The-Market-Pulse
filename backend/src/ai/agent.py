"""LangChain agent for the MarketPulse AI assistant."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.core.config import settings
from src.ai.tools import ALL_TOOLS

SYSTEM_PROMPT = """\
You are **PulseAI**, the intelligent assistant for The Market Pulse — a financial \
blog and market data platform.

Your capabilities:
- Fetch live stock/crypto quotes
- Analyze price history and trends
- Compare multiple assets side-by-side
- Explain financial concepts clearly
- Discuss market news and strategies

Guidelines:
- Be concise, professional, and data-driven
- Use emojis sparingly for clarity (📈📉🔴🟢)
- When asked about a stock, proactively fetch the latest quote
- Format numbers with proper separators ($1,234.56)
- If you're unsure, say so — never fabricate financial data
- Always note: "This is not financial advice"
"""


def create_agent():
    """Create a LangChain agent with market data tools."""
    if not settings.OPENAI_API_KEY:
        return None

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.3,
        streaming=True,
    )

    # Bind tools to the model
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    return {
        "llm": llm_with_tools,
        "prompt": prompt,
        "tools": {t.name: t for t in ALL_TOOLS},
    }


async def run_agent(agent_config: dict, user_input: str, chat_history: list[dict]):
    """
    Run the agent on user input with conversation history.
    Yields chunks of text as they stream back.
    """
    if not agent_config:
        yield "AI assistant is not configured. Please set OPENAI_API_KEY."
        return

    llm = agent_config["llm"]
    prompt = agent_config["prompt"]
    tools = agent_config["tools"]

    # Convert chat history to LangChain messages
    lc_history = []
    for msg in chat_history[-20:]:  # Keep last 20 messages for context
        if msg["role"] == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_history.append(AIMessage(content=msg["content"]))

    messages = prompt.format_messages(
        chat_history=lc_history,
        input=user_input,
        agent_scratchpad=[],
    )

    # Agentic loop: call LLM, check for tool calls, execute, repeat
    max_iterations = 5
    for _ in range(max_iterations):
        # Stream the LLM response
        full_response = ""
        tool_calls = []

        async for chunk in llm.astream(messages):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content
            if chunk.tool_calls:
                tool_calls.extend(chunk.tool_calls)

        # If no tool calls, we're done
        if not tool_calls:
            return

        # Execute tool calls
        messages.append(AIMessage(content=full_response, tool_calls=tool_calls))

        for tc in tool_calls:
            tool_fn = tools.get(tc["name"])
            if tool_fn:
                result = tool_fn.invoke(tc["args"])
                from langchain_core.messages import ToolMessage
                messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
                yield f"\n\n"  # Visual separator between tool result and final response

    yield "\n\n_Reached maximum reasoning steps._"
