from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uuid
from models.llm import llm
from models.chat_models import PromptRequest, BotResponse
from tools.fda_api import query_fda_api
from tools.query_pubmed_api import query_pubmed_api
from tools.usda_api import query_usda_food_data
from tools.disease_prediction import (
    diabetes_prediction_wrapper,
    heart_disease_prediction_wrapper,
    lung_cancer_prediction_wrapper,
    thyroid_prediction_wrapper
)
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
from routes import predictions as predictions_routes

dotenv.load_dotenv()

port = int(os.environ.get("PORT"))

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
else: 
    # Configure CORS for production environment
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://drugsy.web.app",            # Production frontend
            "https://drugsy.firebaseapp.com",    # Alternative production frontend URL
            "https://drugsy-backend-750774374925.us-central1.run.app",  # Backend URL (for API docs)
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include authentication routes
app.include_router(auth_routes.router)

# Include patient routes
app.include_router(patients_routes.router)

# Include prediction routes
app.include_router(predictions_routes.router)

# Define the tools
tools = [
    query_fda_api, 
    query_pubmed_api, 
    query_usda_food_data, 
    diabetes_prediction_wrapper,
    heart_disease_prediction_wrapper,
    lung_cancer_prediction_wrapper,
    thyroid_prediction_wrapper
]

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
        # Add patient information if available
        if patient_info:
            user_info_text += f"\n\nYou are currently reviewing patient: {patient_info['first_name']} {patient_info['last_name']} (the ID of the patient is: {patient_info['id']})\n"
            user_info_text += f"IMPORTANT: When using any patient-related tools, you MUST use the patient ID {patient_info['id']}. Never share the patient id with the user."
            
            # Add patient medication information if available
            if 'medications' in patient_info and patient_info['medications']:
                medications_text = "\n\nThe patient takes the following medications:\n"
                for med in patient_info['medications']:
                    medications_text += f"- {med['name']}: {med['dosage']}, {med['frequency']}\n"
                user_info_text += medications_text
            
            # Add the patient chronic conditions if available
            if 'chronic_conditions' in patient_info and patient_info['chronic_conditions']:
                user_info_text += f"\n\nThe patient has the following chronic conditions:\n{patient_info['chronic_conditions']}"
                
            user_info_text += f"\n\nYou should provide medical advice and information based on this patient's data. Remember to ALWAYS use patient ID {patient_info['id']} when using any patient-related tools."
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

# Helper function to initialize conversation with proper system message
def initialize_conversation(graph, system_prompt, include_welcome=True):
    """
    Initialize a conversation with the proper system message and optional welcome message.
    
    Args:
        graph: The LangGraph instance
        system_prompt: Tuple of (type, content) or just the content
        include_welcome: Whether to include a welcome message
        
    Returns:
        The initialized state
    """
    # Extract system content, handling different formats
    if isinstance(system_prompt, tuple):
        # Extract only the content part of the tuple, ignoring the type
        system_content = system_prompt[1]
    else:
        system_content = system_prompt
    
    # Create initial messages
    initial_messages = [SystemMessage(content=system_content)]
    
    # Add welcome message if requested
    if include_welcome:
        initial_messages.append(AIMessage(content=WELCOME_MSG))
    
    # Initialize the state with these messages
    state = graph.invoke({"messages": initial_messages})
    
    # Debug: Print messages in the state
    print("\n==== INITIAL STATE MESSAGES ====")
    for msg in state["messages"]:
        print(f"Message type: {type(msg).__name__}, content: {msg.content[:50]}...")
    print("================================\n")
    
    return state

# Store conversations by ID - use a more persistent approach
import pickle
import os

# File to store conversations
CONVERSATIONS_FILE = "conversations.pickle"

# Load conversations from file if it exists
def load_conversations():
    if os.path.exists(CONVERSATIONS_FILE):
        try:
            with open(CONVERSATIONS_FILE, "rb") as f:
                loaded_conversations = pickle.load(f)
                return loaded_conversations
        except Exception as e:
            print(f"Error loading conversations: {e}")
    return {}

# Save conversations to file
def save_conversations(conversations_dict):
    try:
        with open(CONVERSATIONS_FILE, "wb") as f:
            pickle.dump(conversations_dict, f)
        print(f"Saved {len(conversations_dict)} conversations to file")
    except Exception as e:
        print(f"Error saving conversations: {e}")

# Initialize conversations
conversations: Dict[str, ApiState] = load_conversations()

# Get welcome message
@app.get("/welcome")
async def get_welcome_message():
    return {"welcome_message": WELCOME_MSG.strip()}

@app.post("/chat", response_model=BotResponse)
async def chat(request: PromptRequest, current_user: schemas.User = Depends(get_current_user_optional)):
    # Generate a new conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())
    # Get or initialize conversation state
    print("\n==== CHAT REQUEST ====")
    print(f"Conversation ID: {conversation_id}")
    print(f"Conversations dictionary ID: {id(conversations)}")
    print(f"Conversations keys: {list(conversations.keys())}")
    print(f"Request conversation_id provided: {request.conversation_id is not None}")
    print(f"Request patient_id: {request.patient_id}")
    # Initialize the conversation state if it doesn't exist
    if conversation_id not in conversations:
        print(f"\n==== INITIALIZING NEW CONVERSATION: {conversation_id} ====")
        # Use the helper function to initialize with system message and welcome message
        state = initialize_conversation(graph_with_tools, DRUG_INTERACTION_BOT)
        conversations[conversation_id] = state
        # Save conversations to file after initialization
        save_conversations(conversations)
        print(f"Conversations after initialization: {list(conversations.keys())}")
    else:
        print(f"\n==== USING EXISTING CONVERSATION: {conversation_id} ====")
        state = conversations[conversation_id]
        print(f"Existing state messages count: {len(state['messages'])}")
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
            # Get patient info if patient_id is provided in the request
            patient_info = None
            if request.patient_id:
                # Import here to avoid circular imports
                from database.crud import get_patient_by_id
                from database.database import get_db
                db = next(get_db())
                patient = get_patient_by_id(db, request.patient_id, current_user.id)
                if patient:
                    patient_info = {
                        'first_name': patient.first_name,
                        'last_name': patient.last_name,
                        'id': patient.id,
                        'medications': patient.medications,
                        'chronic_conditions': patient.chronic_conditions
                    }
            # Create a personalized graph with user and patient information
            if patient_info:
                print(f"Creating personalized graph with patient info: {patient_info['first_name']} {patient_info['last_name']}")
                user_graph = get_graph_with_tools(user_info, patient_info)
            else:
                print("Creating personalized graph with user info only (no patient info)")
                user_graph = get_graph_with_tools(user_info, None)
            
            # Initialize the conversation state if it doesn't exist
            if conversation_id not in conversations:
                # Get the system prompt safely from the graph config
                system_prompt = user_graph.config.get("system_prompt", DRUG_INTERACTION_BOT)
                
                # Use the helper function to initialize with system message and welcome message
                state = initialize_conversation(user_graph, system_prompt)
                conversations[conversation_id] = state
        
        # Process the message with the appropriate graph
        if current_user:
            print(f"\n==== PROCESSING MESSAGE WITH USER: {current_user.email} ====")
            if request.patient_id:
                print(f"Processing with patient ID: {request.patient_id}")
            # Use the personalized graph to process the message
            result_state = process_message(user_graph, state, user_prompt)
        else:
            print(f"\n==== PROCESSING MESSAGE WITHOUT USER ====")
            # Use the default graph to process the message
            result_state = process_message(graph_with_tools, state, user_prompt)
        
        # Store the updated state
        conversations[conversation_id] = result_state
        # Save conversations to file after update
        save_conversations(conversations)
        print(f"\n==== UPDATED CONVERSATION STATE ====")
        print(f"Updated state messages count: {len(result_state['messages'])}")

        # Get the bot's response (last message)
        bot_response = result_state["messages"][-1].content
        print(f"Bot response: {bot_response[:50]}...")
        
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
