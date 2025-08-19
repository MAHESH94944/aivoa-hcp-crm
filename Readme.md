# AI-First HCP CRM

A modern CRM (Customer Relationship Management) system for healthcare professionals (HCPs) that supports both manual and AI-powered workflows. Built with FastAPI, React, Redux Toolkit, and integrates with LLMs for natural language data entry and editing.

---

<div align="center">
  <img src="assets/image.png" alt="Application Screenshot" width="800"/>
  <br/>
  <br/>
  <h1>🤖 AI-First CRM for Healthcare Professionals</h1>
  <p>
    A modern, intelligent Customer Relationship Management (CRM) module designed for life science field representatives to log and manage interactions with Healthcare Professionals (HCPs). This application features a dual-interface system, allowing users to log data through a traditional structured form or a powerful, stateful conversational AI assistant.
  </p>
</div>

---

## ✨ Core Features

- **Dual Data Entry:** Log interactions via a detailed, structured form or by simply describing the interaction in a natural language chat with the AI assistant.
- **Conversational AI Assistant:** A stateful AI co-pilot that can understand, extract, and correct interaction details in real-time. It remembers the context of the conversation to handle follow-up commands.
- **AI-Powered Form Autofill:** Describe a meeting in the chat, and watch the form on the left populate automatically. The AI understands context and can make precise corrections without losing previously entered data.
- **Strategic Insights:** The AI can analyze an HCP's interaction history to provide analytical summaries and suggest strategic next steps, acting as a true digital advisor.
- **Dynamic Suggestions:** As you work with an HCP's record, the "AI Suggested Follow-ups" section automatically updates with relevant, context-aware actions.
- **Advanced Data Retrieval:** Fetch interaction histories using flexible criteria like fuzzy name matching and date-range filtering, complete with pagination.

---

## 🛠️ Technology Stack

| Role         | Technology                                                                                                                                                                                                                                                                                                                                   |
| :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend** | ![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black) ![Redux](https://img.shields.io/badge/Redux-764ABC?logo=redux&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white) |
| **Backend**  | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)                                                                         |
| **Database** | ![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white)                                                                                                                                                                                                                                                               |
| **AI / LLM** | ![LangChain](https://img.shields.io/badge/LangChain-FFFFFF?logo=langchain&logoColor=black) ![Groq](https://img.shields.io/badge/Groq-008639?logo=groq&logoColor=white) (using `gemma2-9b-it`)                                                                                                                                                |

---

## 🧠 The AI Agent System

The core of this application is a system of specialized AI and non-AI "tools" that work together to provide a seamless experience. The system is architected with an agentic design, where each tool has a specific, well-defined purpose.

### 1. **Conversational Tool (`conversation_tool`)**

- **Purpose:** This is the primary tool for the chat assistant. It is a stateful agent that intelligently handles the user's conversational input for data entry and correction.
- **How it Works:** It takes the user's latest message and the current state of the form data as context. Its prompt is designed to extract _only_ the new or changed information from the user's message. The Python code then reliably merges this partial update with the existing data context before returning the full, updated object. This architecture makes the AI's job simpler and the state management 100% reliable.

### 2. **Log Interaction Tool (`log_interaction_tool`)**

- **Purpose:** An advanced, stateless tool designed for one-shot data extraction.
- **How it Works:** It takes a single block of text and uses a highly structured prompt with Chain-of-Thought reasoning and few-shot examples to extract all relevant fields into a perfect JSON object. It is designed to handle missing values gracefully by outputting empty strings, ensuring a consistent data structure.

### 3. **Edit Interaction Tool (`edit_interaction_tool`)**

- **Purpose:** To understand natural language commands for modifying a _saved_ interaction in the database.
- **How it Works:** This is a context-aware tool that takes a user command (e.g., "change the sentiment to Negative") and the existing data of a saved record. It uses a Chain-of-Thought prompt to identify _only_ the fields that need to be changed and returns a partial JSON payload (e.g., `{"sentiment": "Negative"}`), which the backend then uses to perform a targeted database update.

### 4. **Fetch HCP History Tool (`fetch_hcp_history_tool`)**

- **Purpose:** A powerful, non-AI tool for querying the database.
- **How it Works:** This function directly uses SQLAlchemy to query the database. It supports advanced features like fuzzy (case-insensitive) name matching, date range filtering, and full pagination, making it a robust data retrieval engine for both the UI and other AI tools.

### 5. **Summarize History Tool (`summarize_history_tool`)**

- **Purpose:** To provide a deep, analytical summary of an HCP's interaction history.
- **How it Works:** This tool first calls the `fetch_hcp_history_tool` to get the raw data. It then formats this data into a narrative and feeds it to the LLM with an advanced Chain-of-Thought prompt. The AI is instructed to act as a "Senior Medical Science Liaison" and return a structured JSON object containing the relationship status, key takeaways, and a suggested focus for the next meeting.

### 6. **Suggest Next Action Tool (`suggest_next_action_tool`)**

- **Purpose:** To act as a strategic advisor by suggesting proactive next steps.
- **How it Works:** This tool also uses the `fetch_hcp_history_tool` to get the data. It then analyzes key metrics like the time since the last meeting and recent sentiment trends. It feeds this analysis to the LLM with the persona of a "pharmaceutical sales strategist" and asks it to generate three prioritized suggestions, each with a clear rationale explaining _why_ the action is strategic.

---

## 🚀 Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

- Node.js (v18 or later)
- Python (v3.9 or later)
- A running MySQL Server instance

### 1. Backend Setup

```bash
# 1. Clone the repository and navigate to the backend directory
git clone <your-repo-url>
cd <your-repo-name>/backend

# 2. Create and activate a Python virtual environment
python -m venv venv
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# 3. Install all required dependencies from the requirements file
pip install -r requirements.txt

# 4. Set up the database
# Log into your MySQL instance
mysql -u root -p

# Create the database for the project
CREATE DATABASE hcp_crm;
USE hcp_crm;

-- Table creation for hcp_interactions
CREATE TABLE hcp_interactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  hcp_name VARCHAR(255) NOT NULL,
  interaction_type ENUM('Meeting','Call','Virtual') NOT NULL,
  date DATE NOT NULL,
  time TIME NOT NULL,
  attendees JSON,
  topics_discussed TEXT NOT NULL,
  voice_note_summary TEXT,
  materials_shared JSON,
  samples_distributed JSON,
  sentiment ENUM('Positive','Neutral','Negative') NOT NULL,
  outcomes TEXT,
  follow_up_actions JSON,
  ai_suggested_followups JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
exit;

# 5. Configure Environment Variables
# Create a .env file in the /backend directory. You can copy the structure from .env.example if available.
# Add your specific credentials to the .env file:
# DATABASE_URL="mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/hcp_crm"
# GROQ_API_KEY="gsk_YOUR_GROQ_API_KEY_HERE"

# 6. Run the Backend Server
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
# 1. Navigate to the frontend directory in a new terminal
cd ../frontend

# 2. Install all required Node.js dependencies
npm install

# 3. Run the Frontend Development Server
npm run dev
```

The React application will now be running at http://localhost:5173.

---

## 🧪 How to Use and Test the Application

Open the application in your browser at http://localhost:5173.

- **Manual Entry:** Fill out the form on the left and click the "Log Interaction" button to save data directly.

- **AI-Powered Entry:**
  - **Initial Log:** In the AI Assistant chat on the right, type a full description of a meeting.
    - Prompt: Log my meeting with Dr. Evelyn Reed on August 15th, 2025 at 10 AM. We discussed the initial findings for CardioGuard. The sentiment was Neutral as she has some reservations about side effects. The outcome was that she requires more safety data.
    - Observe: The form on the left will automatically populate with the extracted details.
  - **Correction:** Type a follow-up correction into the chat.
    - Prompt: Correction, the outcome was she is 'cautiously optimistic' but still needs the report.
    - Observe: Only the "Outcomes" field will update, preserving all other data.
  - **Save the Interaction:** Click the "Log Interaction" button on the form to save the AI-generated and user-verified data to the database.
  - **Query the AI:** With an HCP's name in the form, use the chat to ask analytical questions.
    - Get History: show me the history for Dr. Evelyn Reed
    - Get Summary: give me a summary for dr. reed
    - Get Suggestions: what are the suggestions for Dr. Reed?
    - Observe: The AI will respond in the chat, and the "AI Suggested Follow-ups" section of the form will update dynamically with the latest strategic advice.

---

## License

MIT
