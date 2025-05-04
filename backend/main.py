from models.llm import llm
from tools.fda_api import query_fda_api

# Import the graph module
from graph.drug_interaction_graph import create_graph
from config.prompts import DRUG_INTERACTION_BOT, WELCOME_MSG

# Define the tools
tools = [query_fda_api]

# Attach the tools to the model so that it knows what it can call.
llm_with_tools = llm.bind_tools(tools)

# Create the graph with our tools and LLM
graph_with_tools = create_graph(
    llm_with_tools=llm_with_tools,
    tools=tools,
    system_prompt=DRUG_INTERACTION_BOT,
    welcome_msg=WELCOME_MSG
)

# Main function to run the application
if __name__ == "__main__":
    try:
        print("Starting Drugsy...")
        
        # Run the graph with an empty initial state
        state = graph_with_tools.invoke({"messages": []}, config={"recursion_limit": 10})
        
        # Main interaction loop
        while not state.get("finished", False):
            # The human_node will display the bot's message and get user input
            state = graph_with_tools.invoke(state, config={"recursion_limit": 10})
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
