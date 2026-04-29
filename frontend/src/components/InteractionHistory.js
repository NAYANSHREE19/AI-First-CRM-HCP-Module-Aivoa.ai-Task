import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  fetchInteractions,
  deleteInteraction,
  setFormData,
  setEditingId,
} from "../store/interactionSlice";
import "./InteractionHistory.css";

export default function InteractionHistory() {
  const dispatch = useDispatch();
  const { list, loading } = useSelector((s) => s.interactions);

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  const handleEdit = (interaction) => {
    dispatch(setEditingId(interaction.id));
    dispatch(
      setFormData({
        hcp_name: interaction.hcp_name || "",
        interaction_type: interaction.interaction_type || "meeting",
        date: interaction.date ? interaction.date.split("T")[0] : "",
        time: interaction.date ? interaction.date.split("T")[1]?.slice(0, 5) : "",
        attendees: interaction.attendees || "",
        topics_discussed: interaction.topics_discussed || "",
        materials_shared: interaction.materials_shared || "",
        samples_distributed: interaction.samples_distributed || "",
        sentiment: interaction.sentiment || "neutral",
        outcomes: interaction.outcomes || "",
        follow_up_actions: interaction.follow_up_actions || "",
      })
    );
  };

  const sentimentBadge = (s) => {
    const map = {
      positive: { emoji: "😊", cls: "positive" },
      neutral: { emoji: "😐", cls: "neutral" },
      negative: { emoji: "😞", cls: "negative" },
    };
    const info = map[s] || map.neutral;
    return <span className={`badge badge-${info.cls}`}>{info.emoji} {s}</span>;
  };

  if (loading) return <div className="history-loading">Loading interactions...</div>;

  return (
    <div className="history-panel">
      <h2 className="history-title">Interaction History</h2>
      {list.length === 0 ? (
        <div className="history-empty">No interactions logged yet.</div>
      ) : (
        <div className="history-list">
          {list.map((item) => (
            <div key={item.id} className="history-card">
              <div className="history-card-header">
                <div>
                  <span className="hcp-name">{item.hcp_name || "Unknown HCP"}</span>
                  <span className="interaction-type">{item.interaction_type}</span>
                </div>
                {sentimentBadge(item.sentiment)}
              </div>

              <div className="history-card-body">
                {item.topics_discussed && (
                  <p><strong>Topics:</strong> {item.topics_discussed}</p>
                )}
                {item.outcomes && (
                  <p><strong>Outcomes:</strong> {item.outcomes}</p>
                )}
                {item.materials_shared && (
                  <p><strong>Materials:</strong> {item.materials_shared}</p>
                )}
                <p className="history-date">
                  {item.date ? new Date(item.date).toLocaleDateString() : "—"}
                </p>
              </div>

              <div className="history-card-actions">
                <button className="btn btn-ghost btn-xs" onClick={() => handleEdit(item)}>
                  ✏️ Edit
                </button>
                <button
                  className="btn btn-ghost btn-xs btn-danger"
                  onClick={() => dispatch(deleteInteraction(item.id))}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
