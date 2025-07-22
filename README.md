# HarmoniAI - Multi-Agent Chatbot System

## Overview

HarmoniAI is a sophisticated, multi-agent chatbot system designed to handle a wide range of tasks by intelligently routing user prompts to specialized agents. It leverages multiple large language models (LLMs) and a vector database to provide accurate, context-aware responses for functionalities including question-answering, content creation, shopping assistance, media recommendations, and more.

The system is built with a FastAPI backend and utilizes the **Model Context Protocol (MCP)** to standardize communication and context-sharing with LLM clients.

## Key Features

- **Multi-Agent Architecture:** Dynamically classifies user intent and delegates tasks to specialized agents (e.g., Shopping, Q&A, Content Creation).
- **Multi-LLM Support:** Integrates with various LLM providers, including OpenAI, Groq, and Google Gemini, allowing for flexibility and optimization.
- **Vector Database Integration:** Uses Weaviate for efficient similarity search and retrieval of contextual data like products and media.
- **Real-time Data Indexing:** Asynchronously fetches and updates its knowledge base from external sources.
- **MCP Compliant:** Implements the Model Context Protocol (via the included `python-sdk`) for standardized interaction with LLM applications.
- **Secure API:** Endpoints are secured using JWT-based authentication.
- **Rich Media Handling:** Capable of processing text, images, and URLs for tasks like image captioning and content generation.

## System Architecture

1.  **FastAPI Server:** The core of the application, serving a RESTful API.
2.  **Authentication:** A JWT-based authentication layer protects the API endpoints.
3.  **Chaining Agent:** The central orchestrator (`chaining_agent.py`) receives user prompts.
4.  **Classifier Agent:** This agent first determines the user's intent (e.g., "shopping", "chat").
5.  **Specialized Agents:** The request is routed to the appropriate agent (e.g., `shopping_agent`, `qa_agent`) for processing.
6.  **LLM Provider:** The selected agent uses the `LLMProvider` service to communicate with an external LLM (like GPT-4, Llama, or Gemini).
7.  **Weaviate Database:** Agents query the Weaviate vector database to retrieve relevant context (e.g., product information, articles) to enrich the prompts.
8.  **Response Generation:** The agent generates a final response, which may include text, data, or recommendations for other models (e.g., suggesting a text-to-image model).

## Technologies Used

- **Backend:** FastAPI, Uvicorn
- **LLM Integration:** OpenAI, Groq, Google Gemini
- **Database:** Weaviate (Vector Database)
- **LLM Communication:** Model Context Protocol (MCP)
- **Scheduling:** APScheduler
- **Authentication:** PyJWT
- **Dependencies:** See `requirements.txt` for a full list.

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd HarmoniAI
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install all the required Python packages.

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

The application requires API keys and other secrets. Create a `.env` file in the root directory of the project. You can copy the example file if one exists, or create a new one.

```bash
# e.g., copy .env.example to .env
cp .env.example .env
```

Now, edit the `.env` file and add your credentials:

```env
# JWT
JWT_ACCESS_SECRET="your_super_secret_jwt_key"

# LLM API Keys
OPENAI_API_KEY="sk-..."
GROQ_API_KEY="gsk_..."
GEMINI_API_KEY="..."

# Weaviate (if applicable)
WEAVIATE_URL="http://localhost:8080"
```

## Running the Application

Once the setup is complete, you can run the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000 --reload
```

The `--reload` flag enables hot-reloading, which is useful for development. The application will be available at `http://localhost:10000`.

## API Documentation

With the server running, interactive API documentation (Swagger UI) is available at:

`http://localhost:10000/docs`

You can use this interface to explore and test the API endpoints. Remember to add your JWT token in the "Authorize" section to access protected routes.

## Project Structure

```
HarmoniAI/
├── app/                  # Main application source code
│   ├── agents/           # Specialized agents for different tasks
│   ├── routes/           # API endpoint definitions
│   ├── services/         # Business logic and external service integrations
│   ├── schemas/          # Pydantic models for data validation
│   ├── main.py           # FastAPI application entry point
│   └── ...
├── python-sdk/           # Model Context Protocol (MCP) SDK
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables (you need to create this)
└── README.md             # This file
```
