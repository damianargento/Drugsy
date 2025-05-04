from typing import TypedDict, Annotated, Literal
from langgraph.graph import add_messages, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages.ai import AIMessage
from langchain_core.messages import HumanMessage, SystemMessage

# Define the state type
class ApiState(TypedDict):
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

def create_api_graph(llm_with_tools, tools, system_prompt, welcome_msg):
    """
    Create the LangGraph for the Drug Interaction Bot API.
    
    Args:
        llm_with_tools: The LLM with tools attached
        tools: List of tools to use
        system_prompt: The system prompt for the bot
        welcome_msg: The welcome message for the bot
        
    Returns:
        The compiled graph
    """
    # Define the tools and create a "tools" node.
    tool_node = ToolNode(tools)
    
    def maybe_route_to_tools(state: ApiState) -> str:
        """Route between tools or end, depending if a tool call is made."""
        if not (msgs := state.get("messages", [])):
            raise ValueError(f"No messages found when parsing state: {state}")
    
        # Only route based on the last message.
        msg = msgs[-1]
    
        # When the chatbot returns tool_calls, route to the "tools" node.
        if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
            return "tools"
        else:
            # Use the END constant from langgraph
            return END
    
    def chatbot_with_tools(state: ApiState) -> ApiState:
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
    
    # Build the graph
    graph_builder = StateGraph(ApiState)
    
    # Add the nodes
    graph_builder.add_node("chatbot", chatbot_with_tools)
    graph_builder.add_node("tools", tool_node)
    
    # Add the edges
    graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    
    # Compile the graph
    return graph_builder.compile()

def process_message(graph, state, message_content):
    """
    Process a single message through the graph and return the result.
    
    Args:
        graph: The compiled graph
        state: The current state
        message_content: The content of the message to process
        
    Returns:
        The updated state after processing the message
    """
    # Create a new state with the message
    if not state:
        # Initialize state if it doesn't exist
        new_state = {"messages": []}
    else:
        # Copy the existing state
        new_state = state.copy()
    
    # Add the message to the state
    new_state["messages"] = new_state["messages"] + [HumanMessage(content=message_content)]
    
    # Process the message through the graph
    result_state = graph.invoke(new_state)
    
    return result_state
