import json
import re
from typing import Dict, Any
from langchain_groq import ChatGroq
from app.core.config import settings
from datetime import date

llm = ChatGroq(temperature=0, model_name="gemma2-9b-it", groq_api_key=settings.GROQ_API_KEY)

def conversation_tool(user_message: str, current_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes a user message to extract partial updates using Chain-of-Thought reasoning,
    then merges them with the current data context in Python for 100% reliability.
    """
    today = date.today().strftime('%Y-%m-%d')
    context_str = json.dumps(current_data, indent=2)

    # This advanced prompt now includes materials and samples.
    prompt = f"""
    You are a hyper-precise conversational data transformation agent. Your task is to analyze a "User Message"
    against a "Current Data Context" and generate a JSON object containing ONLY the fields that need to be updated.

    **Process:**
    1.  First, in a `<thinking>` block, reason through your steps. Identify the user's intent and pinpoint the exact key-value pairs to change.
    2.  After your reasoning, in a ```json block, provide the JSON object containing ONLY the fields that need to be changed or added.

    **CRITICAL RULES:**
    -   Your final JSON output must only contain new or modified data.
    -   For `materials_shared` and `samples_distributed`, the value MUST be a list of strings.
    -   Base any relative dates on the current date: {today}.

    ---
    **CONTEXT: CURRENT DATA**
    {context_str}

    **USER MESSAGE:**
    "{user_message}"
    ---

    **EXAMPLE (Full Extraction with Materials):**
    -   User Message: "Met Dr. Chen today about CardioPlus, it went well. I shared the efficacy brochure and left a starter kit sample."
    -   Your Response:
        <thinking>
        This is a full description. I will extract all relevant fields. 'hcp_name' is Dr. Chen. 'topics_discussed' is CardioPlus. 'sentiment' is Positive. 'date' is today, {today}. The user also mentioned sharing a 'efficacy brochure' and leaving a 'starter kit sample'. I will put these into lists.
        </thinking>
        ```json
        {{
            "hcp_name": "Dr. Chen",
            "topics_discussed": "CardioPlus",
            "sentiment": "Positive",
            "date": "{today}",
            "materials_shared": ["efficacy brochure"],
            "samples_distributed": ["starter kit sample"]
        }}
        ```
    ---

    **YOUR RESPONSE:**
    """
    try:
        # Step 1: Get the partial update from the AI.
        response_content = llm.invoke(prompt).content

        # Robustly find and parse the JSON block from the response
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
        if not json_match:
            json_match = re.search(r"(\{.*?\})", response_content, re.DOTALL)

        if json_match:
            partial_update = json.loads(json_match.group(1))
        else:
            partial_update = {}

        # Step 2: Perform the merge reliably in Python.
        merged_data = current_data.copy()
        
        # Special handling for list fields to append instead of replacing
        for key in ['materials_shared', 'samples_distributed']:
            if key in partial_update:
                existing_list = merged_data.get(key, [])
                new_items = partial_update[key]
                merged_data[key] = existing_list + new_items
                del partial_update[key] # Remove from partial update to avoid double-adding

        merged_data.update(partial_update)

        return {"status": "success", "data": merged_data}
        
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}