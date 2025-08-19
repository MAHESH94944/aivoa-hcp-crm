import os
import json
import re  # <-- FIX 1: Added the missing import for regular expressions
from langchain_groq import ChatGroq
from app.core.config import settings
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import date

# Import the tool we will use to get the data
from .fetch_hcp_history_tool import fetch_hcp_history_tool

# Initialize the LLM
llm = ChatGroq(
    temperature=0.5,
    model_name="gemma2-9b-it",
    groq_api_key=settings.GROQ_API_KEY
)

def suggest_next_action_tool(hcp_name: str, db: Session) -> Dict[str, Any]:
    """
    Analyzes an HCP's interaction history to provide advanced, strategic next steps,
    each with a clear rationale.
    """
    history_result = fetch_hcp_history_tool(hcp_name=hcp_name, db=db)

    if history_result["status"] == "error":
        return history_result

    interactions = history_result["data"]
    today = date.today()

    if not interactions:
        return { "status": "success", "data": { "suggestions": [] } }

    # Step 1: Create a richer, more narrative context for the LLM
    last_interaction_date = interactions[0].date
    days_since_last_meeting = (today - last_interaction_date).days
    
    formatted_history = ""
    for interaction in interactions[:5]: # Analyze the last 5 interactions
        formatted_history += (
            # --- FIX 2: Correctly access .value for both enums ---
            f"- On {interaction.date}, a {interaction.interaction_type.value} with a '{interaction.sentiment.value}' sentiment "
            f"covered '{interaction.topics_discussed}'. Outcome: '{interaction.outcomes}'.\n"
        )

    # Step 2: Use an advanced Chain-of-Thought prompt
    prompt = f"""
    You are an expert pharmaceutical sales strategist and coach. Your task is to analyze an HCP's
    interaction history and generate a JSON object with three prioritized, strategic next steps.

    **Instructions:**
    1.  First, in a `<thinking>` block, perform a strategic analysis of the provided context. Consider:
        -   What is the overall status of the relationship (e.g., advancing, stalling, needs repair)?
        -   What are the key opportunities (e.g., positive sentiment on a key product)?
        -   What are the risks or open questions (e.g., long time since last contact, unaddressed concerns)?
        -   What should the primary goal of the next interaction be?
    2.  After your analysis, provide a JSON object with a single key "suggestions".
    3.  The value for "suggestions" must be a list of three JSON objects.
    4.  Each object must have two keys: "suggestion" (a concrete action) and "rationale" (a brief explanation of why this action is strategic).

    ---
    **CONTEXT FOR {hcp_name}:**
    -   **Days Since Last Interaction:** {days_since_last_meeting}
    -   **Interaction History (most recent first):**
        {formatted_history}
    ---

    **EXAMPLE OUTPUT:**
    <thinking>
    The relationship is advancing well, with positive sentiment on the key product. The main opportunity is to convert this interest into a prescription. The goal is to close the loop on the last discussion.
    </thinking>
    ```json
    {{
      "suggestions": [
        {{
          "suggestion": "Send the full prescribing information for OncoBoost that was requested.",
          "rationale": "This is a direct follow-up to their request and shows you are responsive, moving the conversation forward."
        }},
        {{
          "suggestion": "Propose a brief follow-up call for next week to discuss patient onboarding.",
          "rationale": "This transitions the conversation from data discussion to practical application, indicating a move towards adoption."
        }},
        {{
          "suggestion": "Share a relevant case study of a similar patient profile.",
          "rationale": "Provides additional value and reinforces the product's efficacy in a context that is directly relevant to their practice."
        }}
      ]
    }}
    ```
    ---

    **YOUR RESPONSE:**
    """

    try:
        response_content = llm.invoke(prompt).content
        
        # Robustly find the JSON block in the response
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
        if json_match:
            suggestions = json.loads(json_match.group(1))
            return {"status": "success", "data": suggestions}
        else:
            raise ValueError("No valid JSON block found in the AI's response.")
            
    except Exception as e:
        return {"status": "error", "message": f"AI suggestion generation failed: {str(e)}"}