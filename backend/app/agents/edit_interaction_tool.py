import os
import json
import re
from typing import Dict, Any
from langchain_groq import ChatGroq
from app.core.config import settings
from datetime import date

# Initialize the LLM once to be reused.
llm = ChatGroq(
    temperature=0,
    model_name="gemma2-9b-it",
    groq_api_key=settings.GROQ_API_KEY
)

def edit_interaction_tool(natural_language_command: str, current_interaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a natural language command and the current interaction data, then uses
    Chain-of-Thought reasoning to identify and return a precise JSON update payload.
    """
    today = date.today().strftime('%Y-%m-%d')
    context_str = json.dumps(current_interaction, indent=2, default=str) # Use default=str for dates/times

    prompt = f"""
    You are a hyper-precise data modification agent for a CRM. Your task is to analyze a user's command,
    compare it to the current data for an interaction, and generate a JSON object containing ONLY the fields that need to be changed.

    **Instructions:**
    1.  First, in a `<thinking>` block, analyze the user's command and the current data. Note which specific fields need to be updated and what their new values are.
    2.  If a command is relative (e.g., "tomorrow"), calculate the date based on today: **{today}**.
    3.  After your analysis, provide a JSON object inside a ```json block containing ONLY the fields that need to change. Do not include fields that remain the same.

    ---
    **CONTEXT: CURRENT INTERACTION DATA**
    {context_str}
    ---

    **EXAMPLE:**

    **User Command to Analyze:** "Change the sentiment to Neutral and move the meeting to the 21st."

    **Your Response:**
    <thinking>
    - The user wants to change two fields.
    - The current `sentiment` is 'Positive', the new value should be 'Neutral'.
    - The current `date` is '2025-08-19', the new value should be '2025-08-21'.
    - I will create a JSON object with only these two fields.
    </thinking>
    ```json
    {{
      "sentiment": "Neutral",
      "date": "2025-08-21"
    }}
    ```
    ---

    **Now, process the following request.**

    **User Command to Analyze:** "{natural_language_command}"

    **Your Response:**
    """

    try:
        response_content = llm.invoke(prompt).content

        # Robustly find and parse the JSON block from the response
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
        if json_match:
            update_payload = json.loads(json_match.group(1))
            return {"status": "success", "data": update_payload}
        else:
            raise ValueError("No valid JSON block found in the AI's response.")

    except (json.JSONDecodeError, ValueError) as e:
        return {
            "status": "error",
            "message": f"The AI returned data in an unexpected format. Error: {str(e)}",
            "raw_response": response_content
        }
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}