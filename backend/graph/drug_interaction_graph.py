from typing import TypedDict, Annotated, Literal
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages.ai import AIMessage
from langchain_core.messages import HumanMessage, SystemMessage

# Define the state type
class OrderState(TypedDict):
    """State representing the conversation."""
    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]
    
    # The customer's in-progress order.
    order: list[str]
    
    # Flag indicating that the order is placed and completed.
    finished: bool

def create_graph(llm_with_tools, tools, system_prompt, welcome_msg):
    """
    Create the LangGraph for the Drug Interaction Bot.
    
    Args:
        llm_with_tools: The LLM with tools attached
        tools: List of tools to use
        system_prompt: The system prompt for the bot
        welcome_msg: The welcome message for the bot
        recursion_limit: Maximum number of recursions before stopping
        
    Returns:
        The compiled graph
    """
    # Define the tools and create a "tools" node.
    tool_node = ToolNode(tools)
    
    def maybe_route_to_tools(state: OrderState) -> Literal["tools", "human"]:
        """Route between human or tool nodes, depending if a tool call is made."""
        if not (msgs := state.get("messages", [])):
            raise ValueError(f"No messages found when parsing state: {state}")
    
        # Only route based on the last message.
        msg = msgs[-1]
    
        # When the chatbot returns tool_calls, route to the "tools" node.
        if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
            return "tools"
        else:
            return "human"
    
    def chatbot_with_tools(state: OrderState) -> OrderState:
        """The chatbot with tools. A simple wrapper around the model's own chat interface."""
        defaults = {"order": [], "finished": False}
    
        if state["messages"]:
            # Convert system_prompt tuple to a SystemMessage if it's a tuple
            if isinstance(system_prompt, tuple):
                system_content = system_prompt[1]
                system_message = SystemMessage(content=system_content)
            else:
                system_message = SystemMessage(content=system_prompt)
                
            # Invoke the LLM with the system message and the state messages
            new_output = llm_with_tools.invoke([system_message] + state["messages"])
        else:
            new_output = AIMessage(content=welcome_msg)
    
        # Set up some defaults if not already set, then pass through the provided state,
        # overriding only the "messages" field.
        return defaults | state | {"messages": [new_output]}
    
    def human_node(state: OrderState) -> OrderState:
        """Display the last model message to the user, and receive the user's input."""
        last_msg = state["messages"][-1]
        print("Bot:", last_msg.content)
    
        user_input = input("User: ")
    
        # If it looks like the user is trying to quit, flag the conversation
        # as over.
        if user_input in {"q", "quit", "exit", "goodbye"}:
            state["finished"] = True
    
        return state | {"messages": [HumanMessage(content=user_input)]}
    
    def maybe_exit_human_node(state: OrderState) -> Literal["chatbot", "__end__"]:
        """Route to the chatbot, unless it looks like the user is exiting."""
        if state.get("finished", False):
            return END
        else:
            return "chatbot"
    
    # Build the graph
    graph_builder = StateGraph(OrderState)
    
    # Add the nodes
    graph_builder.add_node("chatbot", chatbot_with_tools)
    graph_builder.add_node("human", human_node)
    graph_builder.add_node("tools", tool_node)
    
    # Add the edges
    graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
    graph_builder.add_conditional_edges("human", maybe_exit_human_node)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    
    # Compile the graph with recursion_limit parameter
    # This is the correct way to set the recursion limit in LangGraph
    return graph_builder.compile()