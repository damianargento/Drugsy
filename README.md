# Drug Interaction Bot

A modern web application that helps users understand how drugs interact with food and other drugs. The application features a React frontend and Python backend that uses the FDA and PubMed APIs to retrieve information about drugs and their interactions, providing reliable and up-to-date information through an easy-to-use interface.

## Features

- Query the FDA and PubMed APIs for comprehensive drug information
- Get detailed information about drug interactions with food and other drugs
- Modern React frontend with responsive design
- RESTful API backend powered by Google's Gemini LLM for natural language understanding
- Real-time API calls to ensure the most current information
- Simple and intuitive user experience

## Project Structure

```
├── backend/                       # Python backend
│   ├── api.py                     # API endpoints
│   ├── main.py                    # Main application entry point
│   ├── config/                    # Configuration
│   │   ├── __init__.py
│   │   └── prompts.py             # System prompts
│   ├── graph/                     # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── api_graph.py           # API graph
│   │   └── drug_interaction_graph.py  # Drug interaction graph
│   ├── models/                    # LLM models
│   │   ├── __init__.py
│   │   └── llm.py                 # LLM configuration
│   └── tools/                     # API tools
│       ├── __init__.py
│       ├── fda_api.py             # FDA API tool
│       └── pubmed_api.py          # PubMed API tool
└── frontend/                      # React frontend
    └── drug-interaction-chat/     # React application
        ├── public/                # Public assets
        │   ├── images/            # Image assets
        │   └── index.html         # HTML entry point
        ├── src/                   # Source code
        │   ├── App.tsx            # Main application component
        │   ├── Chat.css           # Chat styling
        │   ├── index.tsx          # React entry point
        │   └── setupProxy.js       # Proxy configuration
        ├── package.json           # NPM dependencies
        └── tsconfig.json          # TypeScript configuration
```

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/drugsy.git
   cd drugsy
   ```

2. Set up the backend:
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install backend dependencies
   pip install -r backend/requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend/drug-interaction-chat
   npm install
   ```

## Usage

1. Set your Google API key as an environment variable:
   ```bash
   export GOOGLE_API_KEY="your-api-key"
   ```
   
   Or create a `.env` file in the backend directory with:
   ```
   GOOGLE_API_KEY=your-api-key
   ```

2. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

3. In a separate terminal, start the frontend development server:
   ```bash
   cd frontend/drug-interaction-chat
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000` to use the application.

## Deployment

### Backend Deployment

The backend can be deployed to any Python hosting service like Heroku, AWS, or Google Cloud.

### Frontend Deployment

To build the frontend for production:

```bash
cd frontend/drug-interaction-chat
npm run build
```

The build folder can then be deployed to services like Netlify, Vercel, or GitHub Pages.

## Requirements

- Python 3.8 or higher
- Node.js 14.0 or higher
- npm 6.0 or higher
- Google API key for Gemini LLM
- Internet connection for FDA and PubMed API access