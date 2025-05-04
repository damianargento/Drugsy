from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import uuid
from models.llm import llm
from tools.fda_api import query_fda_api
from tools.pubmed_api import query_pubmed_api
from graph.api_graph import create_api_graph, ApiState, process_message
from config.prompts import DRUG_INTERACTION_BOT, WELCOME_MSG
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uvicorn
import os
import dotenv

dotenv.load_dotenv()

app = FastAPI(title="Drug Interaction Bot API")

# Configure CORS for dev mode
if os.getenv("DEV_MODE") == "True":
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Define the tools
tools = [query_fda_api, query_pubmed_api]

# Attach the tools to the model
llm_with_tools = llm.bind_tools(tools)

# Create the API-specific graph with our tools and LLM
graph_with_tools = create_api_graph(
    llm_with_tools=llm_with_tools,
    tools=tools,
    system_prompt=DRUG_INTERACTION_BOT,
    welcome_msg=WELCOME_MSG
)

# Store conversations by ID
conversations: Dict[str, ApiState] = {}

class PromptRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None

class BotResponse(BaseModel):
    response: str
    conversation_id: str

# Get welcome message
@app.get("/welcome")
async def get_welcome_message():
    return {"welcome_message": WELCOME_MSG.strip()}

@app.post("/chat", response_model=BotResponse)
async def chat(request: PromptRequest):
    # Generate a new conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Get or initialize conversation state
    if conversation_id not in conversations:
        # Initialize with welcome message
        state = graph_with_tools.invoke({"messages": []})
        conversations[conversation_id] = state
    else:
        state = conversations[conversation_id]
    
    try:
        # Process the message through the graph
        result_state = process_message(graph_with_tools, state, request.prompt)
        
        # Store the updated state
        conversations[conversation_id] = result_state
        
        # Get the bot's response (last message)
        bot_response = result_state["messages"][-1].content
        
        return BotResponse(
            response=bot_response,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Convert the conversation state to a serializable format
    state = conversations[conversation_id]
    messages = []
    
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
        elif isinstance(msg, SystemMessage):
            messages.append({"role": "system", "content": msg.content})
    
    return {
        "conversation_id": conversation_id,
        "messages": messages,
        "finished": state.get("finished", False)
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=9000, reload=True)
