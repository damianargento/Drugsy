from fastapi import FastAPI, HTTPException, Depends
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

# Database imports
from database import Base, engine
from database.auth import get_current_active_user, get_current_user_optional
from database import schemas
from routes import auth as auth_routes

dotenv.load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

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

# Include authentication routes
app.include_router(auth_routes.router)

# Define the tools
tools = [query_fda_api, query_pubmed_api]

# Attach the tools to the model
llm_with_tools = llm.bind_tools(tools)

# Creamos una función para obtener el grafo con el mensaje de sistema personalizado
def get_graph_with_tools(user_info=None):
    # Si hay información del usuario, personalizamos el mensaje de sistema
    if user_info:
        # Obtenemos el tipo y contenido del mensaje de sistema original
        system_type, system_content = DRUG_INTERACTION_BOT
        
        # Añadimos la información del usuario al principio del mensaje de sistema
        personalized_content = f"El usuario está autenticado. Su nombre es {user_info['first_name']} {user_info['last_name']}. Dirígete a él por su nombre en tus respuestas.\n\n{system_content}"
        
        # Creamos un nuevo mensaje de sistema personalizado
        personalized_system_prompt = (system_type, personalized_content)
        
        # Creamos el grafo con el mensaje de sistema personalizado
        return create_api_graph(
            llm_with_tools=llm_with_tools,
            tools=tools,
            system_prompt=personalized_system_prompt,
            welcome_msg=WELCOME_MSG
        )
    else:
        # Creamos el grafo con el mensaje de sistema original
        return create_api_graph(
            llm_with_tools=llm_with_tools,
            tools=tools,
            system_prompt=DRUG_INTERACTION_BOT,
            welcome_msg=WELCOME_MSG
        )

# Creamos el grafo inicial con el mensaje de sistema original
graph_with_tools = get_graph_with_tools()

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
        # Usamos el prompt original del usuario sin modificar
        user_prompt = request.prompt
        
        # Si el usuario está autenticado y es una nueva conversación, creamos un grafo personalizado
        if current_user and conversation_id not in conversations:
            # Creamos un grafo personalizado con la información del usuario
            user_graph = get_graph_with_tools({
                'first_name': current_user.first_name,
                'last_name': current_user.last_name
            })
            
            # Inicializamos el estado con el grafo personalizado
            state = user_graph.invoke({"messages": []})
            conversations[conversation_id] = state
        # Si el usuario está autenticado, usamos el grafo personalizado
        if current_user and conversation_id in conversations:
            # Usamos el grafo personalizado para procesar el mensaje
            user_graph = get_graph_with_tools({
                'first_name': current_user.first_name,
                'last_name': current_user.last_name
            })
            result_state = process_message(user_graph, state, user_prompt)
        else:
            # Usamos el grafo original para procesar el mensaje
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
    uvicorn.run("api:app", host="0.0.0.0", port=9000, reload=True)
