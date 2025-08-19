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

def log_interaction_tool(natural_language_input: str) -> Dict[str, Any]:
    """
    Takes a natural language sentence about an HCP interaction and uses an advanced
    Chain-of-Thought prompt with few-shot examples to extract structured data.
    """
    today = date.today().strftime('%Y-%m-%d')

    # This advanced prompt forces the LLM to reason before answering.
    prompt = f"""
    You are a hyper-attentive data extraction agent for a CRM. Your task is to analyze a user's text,
    reason through the details step-by-step, and then output a perfect JSON object.

    **Instructions:**
    1.  First, in a `<thinking>` block, analyze the user's text. Identify each piece of information and how it maps to the JSON schema. Note any relative dates and calculate them based on today's date: **{today}**.
    2.  If a value for a field is not mentioned in the text, you MUST use an empty string `""` as its value in the final JSON.
    3.  After your thinking process, provide the final, complete JSON object inside a ```json block. Do not include any other text outside of this block.

    ---
    **EXAMPLE:**
    
    **Text to Analyze:** "Had a quick call with Dr. Carter this morning. It was a neutral conversation about the side effects of CardioPlus. He's not ready to commit."

    **Your Response:**
    <thinking>
    -   **HCP Name:** Dr. Carter is clearly mentioned.
    -   **Interaction Type:** "quick call" indicates "Call".
    -   **Date:** "this morning" implies today's date, which is {today}.
    -   **Time:** "this morning" is ambiguous, I'll use a default of "09:00".
    -   **Attendees:** Only Dr. Carter is mentioned, so I'll list him.
    -   **Topics Discussed:** The topic is "the side effects of CardioPlus".
    -   **Sentiment:** The text says "neutral conversation".
    -   **Outcomes:** The outcome is "He's not ready to commit".
    -   **Follow-up Actions:** No follow-up actions are mentioned, so I will use an empty string.
    </thinking>
    ```json
    {{
        "hcp_name": "Dr. Carter",
        "interaction_type": "Call",
        "date": "{today}",
        "time": "09:00",
        "attendees": "Dr. Carter",
        "topics_discussed": "Side effects of CardioPlus.",
        "sentiment": "Neutral",
        "outcomes": "He is not ready to commit.",
        "follow_up_actions": ""
    }}
    ```
    ---

    **Now, process the following request.**

    **Text to Analyze:** "{natural_language_input}"

    **Your Response:**
    """

    try:
        response_content = llm.invoke(prompt).content

        # This regex is a robust way to find the JSON block, even with surrounding text.
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
        
        if not json_match:
            # Fallback for if the LLM doesn't use the markdown block correctly
            json_match = re.search(r"(\{.*?\})", response_content, re.DOTALL)

        if json_match:
            json_str = json_match.group(1)
            extracted_data = json.loads(json_str)
            return {"status": "success", "data": extracted_data}
        else:
            raise ValueError("No valid JSON object found in the AI's response.")

    except (json.JSONDecodeError, ValueError) as e:
        return {
            "status": "error",
            "message": f"The AI returned data in an unexpected format. Error: {str(e)}",
            "raw_response": response_content
        }
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}