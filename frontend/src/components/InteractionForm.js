import React from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  setFormField,
  createInteraction,
  updateInteraction,
  clearMessages,
} from "../store/interactionSlice";
import "./InteractionForm.css";

const INTERACTION_TYPES = [
  { value: "meeting", label: "Meeting" },
  { value: "call", label: "Call" },
  { value: "email", label: "Email" },
  { value: "conference", label: "Conference" },
];

const SENTIMENTS = [
  { value: "positive", label: "😊 Positive", color: "var(--positive)" },
  { value: "neutral", label: "😐 Neutral", color: "var(--neutral)" },
  { value: "negative", label: "😞 Negative", color: "var(--negative)" },
];

export default function InteractionForm() {
  const dispatch = useDispatch();
  const { formData, saving, editingId, successMessage, error } = useSelector(
    (s) => s.interactions
  );

  const handleChange = (field) => (e) => {
    dispatch(setFormField({ field, value: e.target.value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.hcp_name.trim()) return;

    const payload = { ...formData };
    if (payload.date && payload.time) {
      payload.date = `${payload.date}T${payload.time}:00`;
    }
    delete payload.time;

    if (editingId) {
      dispatch(updateInteraction({ id: editingId, data: payload }));
    } else {
      dispatch(createInteraction(payload));
    }
  };

  return (
    <form className="interaction-form" onSubmit={handleSubmit}>
      {successMessage && (
        <div className="alert alert-success" onClick={() => dispatch(clearMessages())}>
          ✅ {successMessage}
        </div>
      )}
      {error && (
        <div className="alert alert-error" onClick={() => dispatch(clearMessages())}>
          ❌ {error}
        </div>
      )}

      <div className="form-section-label">Interaction Details</div>

      <div className="form-row">
        <div className="form-group">
          <label>HCP Name</label>
          <input
            type="text"
            placeholder="Search or select HCP..."
            value={formData.hcp_name}
            onChange={handleChange("hcp_name")}
            required
          />
        </div>
        <div className="form-group">
          <label>Interaction Type</label>
          <select
            value={formData.interaction_type}
            onChange={handleChange("interaction_type")}
          >
            {INTERACTION_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Date</label>
          <input
            type="date"
            value={formData.date}
            onChange={handleChange("date")}
          />
        </div>
        <div className="form-group">
          <label>Time</label>
          <input
            type="time"
            value={formData.time}
            onChange={handleChange("time")}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Attendees</label>
        <input
          type="text"
          placeholder="Enter names or search..."
          value={formData.attendees}
          onChange={handleChange("attendees")}
        />
      </div>

      <div className="form-group">
        <label>Topics Discussed</label>
        <textarea
          rows={3}
          placeholder="Enter key discussion points..."
          value={formData.topics_discussed}
          onChange={handleChange("topics_discussed")}
        />
      </div>

      <div className="form-section-label">Materials Shared / Samples Distributed</div>

      <div className="form-group">
        <label>Materials Shared</label>
        <input
          type="text"
          placeholder="Brochures, presentations..."
          value={formData.materials_shared}
          onChange={handleChange("materials_shared")}
        />
      </div>

      <div className="form-group">
        <label>Samples Distributed</label>
        <input
          type="text"
          placeholder="Product samples..."
          value={formData.samples_distributed}
          onChange={handleChange("samples_distributed")}
        />
      </div>

      <div className="form-section-label">Observed/Inferred HCP Sentiment</div>
      <div className="sentiment-row">
        {SENTIMENTS.map((s) => (
          <label
            key={s.value}
            className={`sentiment-option ${formData.sentiment === s.value ? "active" : ""}`}
          >
            <input
              type="radio"
              name="sentiment"
              value={s.value}
              checked={formData.sentiment === s.value}
              onChange={handleChange("sentiment")}
            />
            <span>{s.label}</span>
          </label>
        ))}
      </div>

      <div className="form-group">
        <label>Outcomes</label>
        <textarea
          rows={2}
          placeholder="Key outcomes or agreements..."
          value={formData.outcomes}
          onChange={handleChange("outcomes")}
        />
      </div>

      <div className="form-group">
        <label>Follow-up Actions</label>
        <textarea
          rows={2}
          placeholder="Next steps and follow-ups..."
          value={formData.follow_up_actions}
          onChange={handleChange("follow_up_actions")}
        />
      </div>

      <button
        type="submit"
        className="btn btn-primary btn-block"
        disabled={saving || !formData.hcp_name.trim()}
      >
        {saving ? "Saving..." : editingId ? "Update Interaction" : "Log Interaction"}
      </button>
    </form>
  );
}
