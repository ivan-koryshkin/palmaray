from collections.abc import Callable
from typing import Any, Awaitable, List, NotRequired, TypedDict

import attrs
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph


class ConversationState(TypedDict):
    user_message: str
    user_id: int
    topic_id: int
    short_history: NotRequired[List[BaseMessage]]
    long_history: NotRequired[List[dict[str, Any]]]
    messages: NotRequired[List[BaseMessage]]
    response: NotRequired[str]
    message_count: NotRequired[int]


@attrs.frozen(kw_only=True, slots=True)
class LlmRequest:
    llm: ChatOpenAI
    get_short_conversation_history: Callable[[int, int], Awaitable[list[BaseMessage]]]
    get_long_conversation_history: Callable[[int, str], Awaitable[list[str]]]
    archive_conversation_history: Callable[[int], Awaitable[None]]

    async def __call__(self, user_message: str, user_id: int, topic_id: int) -> dict[str, Any]:
        graph = self._create_conversation_graph()
        result = await graph.ainvoke({"user_message": user_message, "user_id": user_id, "topic_id": topic_id})
        await self.archive_conversation_history(topic_id)
        return result

    def _build_system_context(self, long_history: List[dict[str, Any]]) -> str:
        context_parts = [
            "You are a helpful AI assistant. "
            "Answer only in telegram markdown format"
            "Based on previous conversations:"
        ]

        for history_item in long_history:
            summary = history_item.get("summary", "")
            topics = ", ".join(history_item.get("topics", []))
            preferences = ", ".join(history_item.get("preferences", []))

            context_parts.append(f"- {summary}")
            if topics:
                context_parts.append(f"  Topics discussed: {topics}")
            if preferences:
                context_parts.append(f"  User preferences: {preferences}")

        context_parts.append("\nUse this context to provide more personalized and relevant responses.")
        return "\n".join(context_parts)

    async def _get_short_history_node(self, state: ConversationState) -> ConversationState:
        user_id = state["user_id"]
        topic_id = state["topic_id"]
        try:
            short_history = await self.get_short_conversation_history(user_id, topic_id)
        except Exception as ex:
            raise ex
        return {**state, "short_history": short_history}

    async def _get_long_history_node(self, state: ConversationState) -> ConversationState:
        user_id = state["user_id"]
        user_message = state["user_message"]
        long_history = await self.get_long_conversation_history(user_id, user_message)
        return {**state, "long_history": long_history}

    async def _build_context_node(self, state: ConversationState) -> ConversationState:
        messages = []
        long_history = state.get("long_history", [])
        if long_history:
            system_context = self._build_system_context(long_history)
            messages.append(SystemMessage(content=system_context))
        short_history = state.get("short_history", [])
        messages.extend(short_history)
        user_message = state["user_message"]
        messages.append(HumanMessage(content=user_message))
        return {**state, "messages": messages}

    async def _llm_node(self, state: ConversationState) -> ConversationState:
        messages = state["messages"]
        response = await self.llm.ainvoke(messages)
        return {**state, "response": response.content, "message_count": len(messages)}

    def _create_conversation_graph(self) -> StateGraph:
        graph = StateGraph(ConversationState)
        graph.add_node("get_short_history", self._get_short_history_node)
        graph.add_node("get_long_history", self._get_long_history_node)
        graph.add_node("build_context", self._build_context_node)
        graph.add_node("llm_response", self._llm_node)
        
        graph.add_edge(START, "get_short_history")
        graph.add_edge("get_short_history", "get_long_history")
        graph.add_edge("get_long_history", "build_context")
        graph.add_edge("build_context", "llm_response")
        graph.add_edge("llm_response", END)
        return graph.compile()
