from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uuid
from models.llm import llm
from models.chat_models import PromptRequest, BotResponse
from tools.fda_api import query_fda_api
from tools.pubmed_api import query_pubmed_api
from tools.usda_api import query_usda_food_data
from graph.api_graph import create_api_graph, ApiState, process_message
from config.prompts import DRUG_INTERACTION_BOT, WELCOME_MSG
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uvicorn
import os
import dotenv

# Database imports
from database import Base, engine
from database.auth import get_current_active_user, get_current_user_optional
from database import schemas
from routes import auth as auth_routes
from routes import patients as patients_routes

dotenv.load_dotenv()

port = int(os.environ.get("PORT", 8080))

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Drugsy, the healthy chatbot", description="API for drug interaction bot", version="1.0.0")

if os.getenv("DEV_MODE") == "True":
    # Configure CORS for all environments
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include authentication routes
app.include_router(auth_routes.router)

# Include patient routes
app.include_router(patients_routes.router)

# Define the tools
tools = [query_fda_api, query_pubmed_api, query_usda_food_data]

# Attach the tools to the model
llm_with_tools = llm.bind_tools(tools)

# Create a function to get the graph with the personalized system prompt
def get_graph_with_tools(user_info=None, patient_info=None):
    # If there is user information, personalize the system prompt
    if user_info:
        # Get the type and content of the original system prompt
        system_type, system_content = DRUG_INTERACTION_BOT
        
        # Prepare the basic user information
        user_info_text = f"You are assisting Dr. {user_info['first_name']} {user_info['last_name']}."
        print(patient_info)
        # Add patient information if available
        if patient_info:
            user_info_text += f"\n\nYou are currently reviewing patient: {patient_info['first_name']} {patient_info['last_name']}"
            
            # Add patient medication information if available
            if 'medications' in patient_info and patient_info['medications']:
                medications_text = "\n\nThe patient takes the following medications:\n"
                for med in patient_info['medications']:
                    medications_text += f"- {med['name']}: {med['dosage']}, {med['frequency']}\n"
                user_info_text += medications_text
            
            # Add the patient chronic conditions if available
            if 'chronic_conditions' in patient_info and patient_info['chronic_conditions']:
                user_info_text += f"\n\nThe patient has the following chronic conditions:\n{patient_info['chronic_conditions']}"
                
            user_info_text += "\n\nYou should provide medical advice and information based on this patient's data."
        
        # Add personalized information to system prompt
        personalized_content = f"{user_info_text}\n\n{system_content}"
        
        # Create the personalized system prompt
        personalized_system_prompt = (system_type, personalized_content)
        
        # Create the graph with the personalized system prompt
        return create_api_graph(
            llm_with_tools=llm_with_tools,
            tools=tools,
            system_prompt=personalized_system_prompt,
            welcome_msg=WELCOME_MSG
        )
    else:
        # Create the graph with the original system prompt
        return create_api_graph(
            llm_with_tools=llm_with_tools,
            tools=tools,
            system_prompt=DRUG_INTERACTION_BOT,
            welcome_msg=WELCOME_MSG
        )

# Create the initial graph with the original system prompt
graph_with_tools = get_graph_with_tools()

# Store conversations by ID
conversations: Dict[str, ApiState] = {}

# Get welcome message
@app.get("/welcome")
async def get_welcome_message():
    return {"welcome_message": WELCOME_MSG.strip()}

@app.post("/chat", response_model=BotResponse)
async def chat(request: PromptRequest, current_user: schemas.User = Depends(get_current_user_optional)):
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
        # Use the original user prompt without modification
        user_prompt = request.prompt
        
        # If the user is authenticated, prepare user info once for all conditions
        user_graph = graph_with_tools  # Default to original graph
        if current_user:
            # Prepare the basic user information for the personalized graph
            user_info = {
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
            }
            print(request)
            # Get patient info if patient_id is provided in the request
            patient_info = None
            if request.patient_id:
                # Import here to avoid circular imports
                from database.crud import get_patient_by_id
                from database.database import get_db
                db = next(get_db())
                patient = get_patient_by_id(db, request.patient_id, current_user.id)
                print(patient)
                if patient:
                    patient_info = {
                        'first_name': patient.first_name,
                        'last_name': patient.last_name,
                        'medications': patient.medications,
                        'chronic_conditions': patient.chronic_conditions
                    }
            
            # Create a personalized graph with user and patient information
            user_graph = get_graph_with_tools(user_info, patient_info)
            
            # If it's a new conversation, initialize the state with the personalized graph
            if conversation_id not in conversations:
                state = user_graph.invoke({"messages": []})
                conversations[conversation_id] = state
        
        # Process the message with the appropriate graph
        if current_user:
            # Use the personalized graph to process the message
            result_state = process_message(user_graph, state, user_prompt)
        else:
            # Use the original graph to process the message
            result_state = process_message(graph_with_tools, state, user_prompt)
        
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
async def get_conversation(conversation_id: str, current_user: schemas.User = Depends(get_current_active_user)):
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
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
