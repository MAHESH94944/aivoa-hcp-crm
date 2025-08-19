import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/interactions"; // Base URL

// --- All your thunks are correct ---

export const createInteraction = createAsyncThunk(
  "interactions/create",
  async (interactionData, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/`, interactionData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || "An error occurred");
    }
  }
);

export const sendChatMessage = createAsyncThunk(
  "interactions/sendChatMessage",
  async (message, { getState, rejectWithValue }) => {
    const { interactions } = getState();
    const current_data = interactions.formData;
    try {
      const response = await axios.post(`${API_URL}/ai/conversation`, {
        message,
        current_data,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || "AI chat failed");
    }
  }
);

export const fetchHistory = createAsyncThunk(
  "interactions/fetchHistory",
  async (hcpName, { rejectWithValue }) => {
    try {
      const response = await axios.get(
        `${API_URL}/ai/history/${encodeURIComponent(hcpName)}`
      );
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const fetchSummary = createAsyncThunk(
  "interactions/fetchSummary",
  async (hcpName, { rejectWithValue }) => {
    try {
      const response = await axios.get(
        `${API_URL}/ai/summary/${encodeURIComponent(hcpName)}`
      );
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const fetchSuggestions = createAsyncThunk(
  "interactions/fetchSuggestions",
  async (hcpName, { rejectWithValue }) => {
    try {
      const response = await axios.get(
        `${API_URL}/ai/suggestions/${encodeURIComponent(hcpName)}`
      );
      return response.data.suggestions;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

const initialState = {
  formData: {
    hcp_name: "",
    interaction_type: "Meeting",
    date: new Date().toISOString().split("T")[0],
    time: new Date().toTimeString().substring(0, 5),
    attendees: "",
    topics_discussed: "",
    sentiment: "Neutral",
    outcomes: "",
    follow_up_actions: "",
    materials_shared: [], // Should be an array
    samples_distributed: [], // Should be an array
  },
  messages: [],
  items: [],
  history: [],
  summary: null,
  suggestions: [],
  status: "idle",
  error: null,
};

const interactionsSlice = createSlice({
  name: "interactions",
  initialState,
  reducers: {
    setFormData: (state, action) => {
      state.formData = { ...state.formData, ...action.payload };
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      // --- Other cases are correct ---
      .addCase(createInteraction.pending, (state) => {
        state.status = "loading";
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items.push(action.payload);
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })
      .addCase(sendChatMessage.pending, (state) => {
        state.status = "loading";
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.formData = { ...state.formData, ...action.payload };
        state.messages.push({
          sender: "ai",
          text: "OK, I've updated the details. Is there anything else?",
        });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
        state.messages.push({
          sender: "ai",
          text: "Sorry, I couldn't process that. Please try rephrasing.",
        });
      })
      .addCase(fetchHistory.fulfilled, (state, action) => {
        const historyText = action.payload.data
          .map(
            (item) =>
              `On ${item.date}: A ${item.interaction_type} about "${item.topics_discussed}" resulted in "${item.outcomes}".`
          )
          .join("\n");
        state.messages.push({
          sender: "ai",
          text: `Here is the history for ${action.meta.arg}:\n${historyText}`,
        });
      })

      // --- THIS CASE IS NOW FIXED ---
      .addCase(fetchSummary.fulfilled, (state, action) => {
        // The summary object is the payload itself, not payload.data
        const summary = action.payload;
        const summaryText = `Status: ${
          summary.relationship_status
        }\n\nTakeaways:\n- ${summary.key_takeaways.join("\n- ")}\n\nFocus: ${
          summary.suggested_focus
        }`;
        state.messages.push({
          sender: "ai",
          text: `Here is the summary for ${action.meta.arg}:\n${summaryText}`,
        });
      })
      .addCase(fetchSuggestions.fulfilled, (state, action) => {
        state.suggestions = action.payload;
        state.messages.push({
          sender: "ai",
          text: `I've updated the suggested next steps based on the history.`,
        });
      });
  },
});

export const { setFormData, addMessage } = interactionsSlice.actions;
export default interactionsSlice.reducer;
