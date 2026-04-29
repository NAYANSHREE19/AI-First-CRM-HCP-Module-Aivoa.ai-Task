import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../api/axios";

// Async thunks
export const fetchInteractions = createAsyncThunk(
  "interactions/fetchAll",
  async (_, { rejectWithValue }) => {
    try {
      const res = await api.get("/interactions/");
      return res.data;
    } catch (e) {
      return rejectWithValue(e.response?.data?.detail || "Failed to fetch");
    }
  }
);

export const createInteraction = createAsyncThunk(
  "interactions/create",
  async (data, { rejectWithValue }) => {
    try {
      const res = await api.post("/interactions/", data);
      return res.data;
    } catch (e) {
      return rejectWithValue(e.response?.data?.detail || "Failed to create");
    }
  }
);

export const updateInteraction = createAsyncThunk(
  "interactions/update",
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const res = await api.put(`/interactions/${id}`, data);
      return res.data;
    } catch (e) {
      return rejectWithValue(e.response?.data?.detail || "Failed to update");
    }
  }
);

export const deleteInteraction = createAsyncThunk(
  "interactions/delete",
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/interactions/${id}`);
      return id;
    } catch (e) {
      return rejectWithValue(e.response?.data?.detail || "Failed to delete");
    }
  }
);

const initialFormData = {
  hcp_name: "",
  interaction_type: "meeting",
  date: new Date().toISOString().split("T")[0],
  time: new Date().toTimeString().slice(0, 5),
  attendees: "",
  topics_discussed: "",
  materials_shared: "",
  samples_distributed: "",
  sentiment: "neutral",
  outcomes: "",
  follow_up_actions: "",
};

const interactionSlice = createSlice({
  name: "interactions",
  initialState: {
    list: [],
    formData: { ...initialFormData },
    loading: false,
    saving: false,
    error: null,
    successMessage: null,
    editingId: null,
  },
  reducers: {
    setFormField: (state, action) => {
      const { field, value } = action.payload;
      state.formData[field] = value;
    },
    setFormData: (state, action) => {
      state.formData = { ...state.formData, ...action.payload };
    },
    resetForm: (state) => {
      state.formData = { ...initialFormData };
      state.editingId = null;
      state.successMessage = null;
      state.error = null;
    },
    setEditingId: (state, action) => {
      state.editingId = action.payload;
    },
    clearMessages: (state) => {
      state.successMessage = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => { state.loading = true; })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createInteraction.pending, (state) => { state.saving = true; })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.saving = false;
        state.list.unshift(action.payload);
        state.successMessage = "Interaction logged successfully!";
        state.formData = { ...initialFormData };
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.saving = false;
        state.error = action.payload;
      })
      .addCase(updateInteraction.pending, (state) => { state.saving = true; })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        state.saving = false;
        const idx = state.list.findIndex(i => i.id === action.payload.id);
        if (idx !== -1) state.list[idx] = action.payload;
        state.successMessage = "Interaction updated!";
        state.editingId = null;
      })
      .addCase(updateInteraction.rejected, (state, action) => {
        state.saving = false;
        state.error = action.payload;
      })
      .addCase(deleteInteraction.fulfilled, (state, action) => {
        state.list = state.list.filter(i => i.id !== action.payload);
      });
  },
});

export const { setFormField, setFormData, resetForm, setEditingId, clearMessages } = interactionSlice.actions;
export default interactionSlice.reducer;
