import os
import json
import re
from langchain_groq import ChatGroq
from app.core.config import settings
from sqlalchemy.orm import Session
from typing import Dict, Any

# Import the other tool we need to use
from .fetch_hcp_history_tool import fetch_hcp_history_tool

# Initialize the LLM
llm = ChatGroq(
    temperature=0,
    model_name="gemma2-9b-it",
    groq_api_key=settings.GROQ_API_KEY
)

def summarize_history_tool(hcp_name: str, db: Session) -> Dict[str, Any]:
    """
    Generates an advanced, structured summary of an HCP's interaction history
    using Chain-of-Thought reasoning.
    """
    # Step 1: Call the Fetch History Tool to get the data
    history_result = fetch_hcp_history_tool(hcp_name=hcp_name, db=db)

    if history_result["status"] == "error":
        return history_result

    interactions = history_result["data"]

    if not interactions:
        return {
            "status": "success",
            "data": {
                "relationship_status": "New Relationship",
                "key_takeaways": ["No prior interactions logged."],
                "suggested_focus": "Initial engagement and needs assessment."
            }
        }

    # Step 2: Format the fetched data into a readable string for the LLM
    formatted_history = ""
    for interaction in interactions[:5]: # Analyze the last 5 interactions
        formatted_history += (
            f"- On {interaction.date}, a {interaction.interaction_type.value} with a '{interaction.sentiment.value}' sentiment "
            f"covered '{interaction.topics_discussed}'. Outcome: '{interaction.outcomes}'.\n"
        )

    # Step 3: Create an advanced Chain-of-Thought prompt
    prompt = f"""
    You are a Senior Medical Science Liaison providing a pre-meeting briefing to a sales representative.
    Your task is to analyze the following interaction history and generate a structured JSON summary.

    **Instructions:**
    1.  First, in a `<thinking>` block, analyze the history. Identify the overall sentiment trend, recurring topics, the last outcome, and the general state of the relationship.
    2.  After your analysis, provide a JSON object with three keys: `relationship_status`, `key_takeaways` (a list of 2-3 bullet points), and `suggested_focus` (a single sentence for the next meeting).

    ---
    **Interaction History for {hcp_name}:**
    {formatted_history}
    ---

    **EXAMPLE OUTPUT:**
    <thinking>
    The sentiment trend is positive and consistent. The main topic is clearly OncoBoost's efficacy data. The last outcome was a commitment to start patients, which is a strong buying signal. The relationship is advancing well. The focus should be on enabling their first prescription.
    </thinking>
    ```json
    {{
      "relationship_status": "Advancing Positively",
      "key_takeaways": [
        "Consistently positive sentiment towards OncoBoost.",
        "High interest in clinical trial data and patient eligibility.",
        "Recent commitment to prescribe indicates readiness to adopt."
      ],
      "suggested_focus": "Focus the next conversation on patient onboarding and logistical support to ensure a smooth first prescription."
    }}
    ```
    ---

    **YOUR RESPONSE:**
    """

    try:
        response_content = llm.invoke(prompt).content

        # Robustly find and parse the JSON block from the response
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
        if json_match:
            summary_data = json.loads(json_match.group(1))
            return {"status": "success", "data": summary_data}
        else:
            raise ValueError("No valid JSON block found in the AI's response.")

    except Exception as e:
        return {"status": "error", "message": f"AI summary generation failed: {str(e)}"}