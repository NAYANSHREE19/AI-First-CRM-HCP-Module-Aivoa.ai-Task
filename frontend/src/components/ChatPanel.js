import React, { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendChatMessage, addUserMessage, clearChat } from "../store/chatSlice";
import { setFormData } from "../store/interactionSlice";
import "./ChatPanel.css";

export default function ChatPanel() {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((s) => s.chat);
  const formData = useSelector((s) => s.interactions.formData);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* When AI returns form_updates, push them into the interaction form */
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (last?.role === "assistant" && last.formUpdates) {
      dispatch(setFormData(last.formUpdates));
    }
  }, [messages, dispatch]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    dispatch(addUserMessage(text));

    const history = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    dispatch(sendChatMessage({ message: text, history, formData }));
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-left">
          <span className="chat-icon">🤖</span>
          <div>
            <h3>AI Assistant</h3>
            <p className="chat-subtitle">Log interaction details here via chat</p>
          </div>
        </div>
        <button className="btn btn-ghost btn-xs" onClick={() => dispatch(clearChat())}>
          Clear
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-hint">
            Log interaction details here (e.g., "Met Dr. Smith, discussed
            Prodo-X efficacy, positive sentiment, shared brochure") or ask for
            help.
          </div>
        )}

        {messages.map((m) => (
          <div key={m.id} className={`chat-bubble ${m.role}`}>
            <span className="bubble-text">{m.content}</span>
            {m.action && (
              <span className="bubble-badge">
                {m.action === "logged" ? "✅ Logged" : "✏️ Updated"}
              </span>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble assistant typing">
            <span className="dot" /><span className="dot" /><span className="dot" />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-row">
        <input
          type="text"
          className="chat-input"
          placeholder="Describe interaction..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className="btn btn-primary btn-send"
          onClick={handleSend}
          disabled={!input.trim() || loading}
        >
          <span className="send-label">A</span>
          <span className="send-sub">Log</span>
        </button>
      </div>
    </div>
  );
}
