from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import date
from pydantic import BaseModel

# Local application imports
from .. import crud, models, schemas
from ..database import get_db

# Import all AI agent tools
from ..agents.conversation_tool import conversation_tool
from ..agents.edit_interaction_tool import edit_interaction_tool
from ..agents.fetch_hcp_history_tool import fetch_hcp_history_tool
from ..agents.summarize_history_tool import summarize_history_tool
from ..agents.suggest_next_action_tool import suggest_next_action_tool

# Initialize the router
router = APIRouter(
    prefix="/interactions",
    tags=["HCP Interactions"]
)

# Pydantic model for the stateful conversation request
class ConversationRequest(BaseModel):
    message: str
    current_data: Dict[str, Any]

# --- Manual CRM Endpoints ---

@router.post("/", response_model=schemas.InteractionOut, status_code=201, summary="Log Interaction via Form")
def create_new_interaction(interaction: schemas.InteractionCreate, db: Session = Depends(get_db)):
    """Creates a new HCP interaction from the structured web form."""
    return crud.create_interaction(db=db, interaction=interaction)

@router.get("/", response_model=List[schemas.InteractionOut], summary="Get All Interactions")
def read_all_interactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieves all HCP interactions with pagination."""
    return crud.get_all_interactions(db, skip=skip, limit=limit)

# --- AI Agent Endpoints ---

@router.post("/ai/conversation", summary="Handle Conversational AI Chat")
def handle_conversation(request: ConversationRequest):
    """
    Manages the stateful conversation, taking the user's message and
    the current form data to provide a context-aware response.
    """
    result = conversation_tool(
        user_message=request.message,
        current_data=request.current_data
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result["data"]

@router.patch("/ai/{interaction_id}", response_model=schemas.InteractionOut, summary="Edit Saved Interaction via AI")
def update_saved_interaction_from_text(
    interaction_id: int,
    command: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Updates a saved HCP interaction using a natural language command."""
    # 1. Fetch the existing record
    db_interaction = crud.get_interaction(db, interaction_id=interaction_id)
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    # 2. Convert the record to a dictionary to provide as context
    current_data = schemas.InteractionOut.from_orm(db_interaction).model_dump()

    # 3. Call the advanced AI tool with the command AND the current data
    result = edit_interaction_tool(
        natural_language_command=command,
        current_interaction=current_data
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    # 4. Apply the partial update returned by the AI
    update_data = result["data"]
    for field, value in update_data.items():
        if hasattr(db_interaction, field):
            setattr(db_interaction, field, value)

    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@router.get("/ai/history/{hcp_name}", response_model=schemas.PaginatedHistoryResponse, summary="Fetch Advanced Interaction History")
def get_interaction_history(
    hcp_name: str,
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 10
):
    """
    Retrieves a paginated and filtered interaction history for a specific HCP.
    Example: /interactions/ai/history/Rossi?start_date=2025-01-01&page=1
    """
    result = fetch_hcp_history_tool(
        db=db, hcp_name=hcp_name, start_date=start_date,
        end_date=end_date, page=page, page_size=page_size
    )
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/ai/summary/{hcp_name}", response_model=Dict[str, Any], summary="Summarize History via AI")
def get_interaction_summary(hcp_name: str, db: Session = Depends(get_db)):
    """Generates an AI-powered summary of an HCP's interaction history."""
    result = summarize_history_tool(hcp_name=hcp_name, db=db)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result.get("data", {"summary": "No summary generated."})

@router.get("/ai/suggestions/{hcp_name}", response_model=Dict[str, Any], summary="Get AI Suggestions")
def get_next_action_suggestions(hcp_name: str, db: Session = Depends(get_db)):
    """Generates a list of AI-powered next-step suggestions for an HCP."""
    result = suggest_next_action_tool(hcp_name=hcp_name, db=db)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result.get("data", {"suggestions": []})