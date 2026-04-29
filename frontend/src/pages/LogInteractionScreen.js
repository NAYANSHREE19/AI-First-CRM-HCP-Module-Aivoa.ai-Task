import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { fetchInteractions, resetForm } from "../store/interactionSlice";
import InteractionForm from "../components/InteractionForm";
import ChatPanel from "../components/ChatPanel";
import InteractionHistory from "../components/InteractionHistory";
import "./LogInteractionScreen.css";

export default function LogInteractionScreen() {
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState("log"); // log | history

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  return (
    <div className="screen-root">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">⚕</span>
            <span className="logo-text">HCP<span className="logo-accent">CRM</span></span>
          </div>
          <nav className="header-nav">
            <button
              className={`nav-btn ${activeTab === "log" ? "active" : ""}`}
              onClick={() => setActiveTab("log")}
            >
              <span>📝</span> Log Interaction
            </button>
            <button
              className={`nav-btn ${activeTab === "history" ? "active" : ""}`}
              onClick={() => setActiveTab("history")}
            >
              <span>📋</span> History
            </button>
          </nav>
        </div>
        <div className="header-right">
          <div className="user-badge">
            <div className="user-avatar">SR</div>
            <span className="user-name">Sales Rep</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-layout">
        {activeTab === "log" ? (
          <>
            {/* Left: Form */}
            <section className="form-section">
              <div className="section-header">
                <h1 className="section-title">Log HCP Interaction</h1>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => dispatch(resetForm())}
                >
                  ↺ Reset
                </button>
              </div>
              <InteractionForm />
            </section>

            {/* Right: Chat */}
            <aside className="chat-section">
              <ChatPanel />
            </aside>
          </>
        ) : (
          <section className="history-section">
            <InteractionHistory />
          </section>
        )}
      </main>
    </div>
  );
}
