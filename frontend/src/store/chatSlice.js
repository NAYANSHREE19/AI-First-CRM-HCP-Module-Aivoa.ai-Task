import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../api/axios";

export const sendChatMessage = createAsyncThunk(
  "chat/send",
  async ({ message, history, formData }, { rejectWithValue }) => {
    try {
      const res = await api.post("/chat/", {
        message,
        conversation_history: history,
        current_form_data: formData,
      });
      return res.data;
    } catch (e) {
      return rejectWithValue(e.response?.data?.detail || "Chat error");
    }
  }
);

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    messages: [],
    loading: false,
    error: null,
  },
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({ role: "user", content: action.payload, id: Date.now() });
    },
    clearChat: (state) => {
      state.messages = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.messages.push({
          role: "assistant",
          content: action.payload.reply,
          formUpdates: action.payload.form_updates,
          action: action.payload.action,
          interactionId: action.payload.interaction_id,
          id: Date.now(),
        });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.messages.push({
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
          id: Date.now(),
        });
      });
  },
});

export const { addUserMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
