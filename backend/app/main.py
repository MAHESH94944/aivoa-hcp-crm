from fastapi import FastAPI
from .database import engine, Base
from .routers import interactions  # Import the consolidated router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-First HCP CRM Backend",
    description="A CRM backend powered by FastAPI and AI Agent Tools.",
    version="1.0.0"
)

# Add CORS middleware to allow communication with the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. In production, list your frontend's domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the API routes from the interactions router
app.include_router(interactions.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "AI-First CRM Backend is running"}