"""
LangGraph AI Agent for HCP CRM
Tools:
1. log_interaction - Parse natural language and log a new interaction
2. edit_interaction - Modify an existing logged interaction
3. search_hcp - Search for HCPs in the database
4. suggest_follow_up - Suggest follow-up actions based on interaction sentiment/context
5. summarize_interaction_history - Summarize all past interactions with an HCP
"""

import os
import json
from datetime import datetime
from typing import Annotated, TypedDict, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from sqlalchemy.orm import Session
from app.models import Interaction, HCP
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"


# --- State ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    form_updates: Optional[dict]
    action: Optional[str]
    interaction_id: Optional[int]
    db_session: Optional[object]


# --- Global DB session holder (set before agent call) ---
_db_session: Optional[Session] = None


def set_db_session(db: Session):
    global _db_session
    _db_session = db


# --- TOOL 1: Log Interaction ---
@tool
def log_interaction(
    hcp_name: str,
    interaction_type: str = "meeting",
    date: str = None,
    topics_discussed: str = None,
    materials_shared: str = None,
    samples_distributed: str = None,
    sentiment: str = "neutral",
    outcomes: str = None,
    follow_up_actions: str = None,
    attendees: str = None,
) -> dict:
    """
    Log a new HCP interaction to the database. Use this when the user describes
    a meeting, call, or any interaction with a Healthcare Professional.
    Extracts entities like HCP name, topics, sentiment, materials, and outcomes.
    Returns the created interaction ID and a summary of what was logged.
    """
    global _db_session
    if not _db_session:
        return {"error": "Database not available", "success": False}

    try:
        interaction_date = datetime.utcnow()
        if date:
            try:
                interaction_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                pass

        interaction = Interaction(
            hcp_name=hcp_name,
            interaction_type=interaction_type,
            date=interaction_date,
            attendees=attendees,
            topics_discussed=topics_discussed,
            materials_shared=materials_shared,
            samples_distributed=samples_distributed,
            sentiment=sentiment,
            outcomes=outcomes,
            follow_up_actions=follow_up_actions,
        )
        _db_session.add(interaction)
        _db_session.commit()
        _db_session.refresh(interaction)

        return {
            "success": True,
            "interaction_id": interaction.id,
            "message": f"Interaction with {hcp_name} logged successfully (ID: {interaction.id})",
            "form_updates": {
                "hcp_name": hcp_name,
                "interaction_type": interaction_type,
                "topics_discussed": topics_discussed or "",
                "materials_shared": materials_shared or "",
                "samples_distributed": samples_distributed or "",
                "sentiment": sentiment,
                "outcomes": outcomes or "",
                "follow_up_actions": follow_up_actions or "",
                "attendees": attendees or "",
            }
        }
    except Exception as e:
        _db_session.rollback()
        return {"error": str(e), "success": False}


# --- TOOL 2: Edit Interaction ---
@tool
def edit_interaction(
    interaction_id: int,
    hcp_name: str = None,
    interaction_type: str = None,
    topics_discussed: str = None,
    materials_shared: str = None,
    samples_distributed: str = None,
    sentiment: str = None,
    outcomes: str = None,
    follow_up_actions: str = None,
    attendees: str = None,
) -> dict:
    """
    Edit/modify an existing logged HCP interaction by its ID.
    Only updates fields that are provided (non-None). Use this when the user
    wants to correct or add information to a previously logged interaction.
    Returns success status and what was changed.
    """
    global _db_session
    if not _db_session:
        return {"error": "Database not available", "success": False}

    try:
        interaction = _db_session.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return {"error": f"Interaction ID {interaction_id} not found", "success": False}

        updates = {}
        if hcp_name is not None:
            interaction.hcp_name = hcp_name
            updates["hcp_name"] = hcp_name
        if interaction_type is not None:
            interaction.interaction_type = interaction_type
            updates["interaction_type"] = interaction_type
        if topics_discussed is not None:
            interaction.topics_discussed = topics_discussed
            updates["topics_discussed"] = topics_discussed
        if materials_shared is not None:
            interaction.materials_shared = materials_shared
            updates["materials_shared"] = materials_shared
        if samples_distributed is not None:
            interaction.samples_distributed = samples_distributed
            updates["samples_distributed"] = samples_distributed
        if sentiment is not None:
            interaction.sentiment = sentiment
            updates["sentiment"] = sentiment
        if outcomes is not None:
            interaction.outcomes = outcomes
            updates["outcomes"] = outcomes
        if follow_up_actions is not None:
            interaction.follow_up_actions = follow_up_actions
            updates["follow_up_actions"] = follow_up_actions
        if attendees is not None:
            interaction.attendees = attendees
            updates["attendees"] = attendees

        interaction.updated_at = datetime.utcnow()
        _db_session.commit()

        return {
            "success": True,
            "interaction_id": interaction_id,
            "updated_fields": updates,
            "message": f"Interaction {interaction_id} updated successfully",
            "form_updates": updates
        }
    except Exception as e:
        _db_session.rollback()
        return {"error": str(e), "success": False}


# --- TOOL 3: Search HCP ---
@tool
def search_hcp(query: str) -> dict:
    """
    Search for Healthcare Professionals (HCPs) in the database by name,
    specialty, institution, or email. Returns a list of matching HCPs
    with their details. Use this to look up HCP information or verify
    if an HCP exists before logging an interaction.
    """
    global _db_session
    if not _db_session:
        return {"error": "Database not available", "hcps": []}

    try:
        hcps = _db_session.query(HCP).filter(
            HCP.name.ilike(f"%{query}%") |
            HCP.specialty.ilike(f"%{query}%") |
            HCP.institution.ilike(f"%{query}%")
        ).limit(10).all()

        results = [
            {
                "id": h.id,
                "name": h.name,
                "specialty": h.specialty,
                "institution": h.institution,
                "email": h.email,
            }
            for h in hcps
        ]
        return {
            "success": True,
            "count": len(results),
            "hcps": results,
            "message": f"Found {len(results)} HCP(s) matching '{query}'"
        }
    except Exception as e:
        return {"error": str(e), "hcps": []}


# --- TOOL 4: Suggest Follow-Up ---
@tool
def suggest_follow_up(
    hcp_name: str,
    sentiment: str,
    topics_discussed: str,
    outcomes: str = None,
) -> dict:
    """
    Suggest intelligent follow-up actions for a sales rep based on the
    HCP interaction details. Considers sentiment (positive/neutral/negative),
    topics discussed, and outcomes to recommend next steps like scheduling
    meetings, sending materials, or escalating concerns.
    Returns a list of specific, actionable follow-up recommendations.
    """
    suggestions = []
    sentiment_lower = (sentiment or "neutral").lower()
    topics_lower = (topics_discussed or "").lower()

    if sentiment_lower == "positive":
        suggestions.append("Schedule a follow-up meeting within 2 weeks to maintain momentum.")
        suggestions.append("Send a thank-you email with relevant product literature or study data.")
        if "sample" in topics_lower or "trial" in topics_lower:
            suggestions.append("Follow up on sample usage and request feedback after 1 week.")
    elif sentiment_lower == "neutral":
        suggestions.append("Send additional supporting materials addressing any unresolved questions.")
        suggestions.append("Schedule a follow-up call in 3-4 weeks to check in.")
        suggestions.append("Consider involving a Medical Science Liaison (MSL) for deeper clinical discussions.")
    elif sentiment_lower == "negative":
        suggestions.append("Flag this interaction for manager review and coaching support.")
        suggestions.append("Wait 4-6 weeks before re-engaging; review objection handling strategies.")
        suggestions.append("Send a brief acknowledgment email showing you heard their concerns.")

    if "brochure" in topics_lower or "material" in topics_lower:
        suggestions.append("Confirm materials were received and answer any questions within 48 hours.")
    if "conference" in topics_lower or "event" in topics_lower:
        suggestions.append("Invite the HCP to the next relevant industry conference or webinar.")

    return {
        "success": True,
        "hcp_name": hcp_name,
        "sentiment": sentiment,
        "suggestions": suggestions,
        "message": f"Generated {len(suggestions)} follow-up suggestions for interaction with {hcp_name}"
    }


# --- TOOL 5: Summarize Interaction History ---
@tool
def summarize_interaction_history(hcp_name: str, limit: int = 10) -> dict:
    """
    Retrieve and summarize the complete interaction history with a specific HCP.
    Provides a chronological overview of all past interactions, sentiment trends,
    topics covered, materials shared, and relationship status. Use this when
    the user wants a briefing before a meeting or wants to understand the
    relationship history with an HCP.
    """
    global _db_session
    if not _db_session:
        return {"error": "Database not available", "summary": ""}

    try:
        interactions = (
            _db_session.query(Interaction)
            .filter(Interaction.hcp_name.ilike(f"%{hcp_name}%"))
            .order_by(Interaction.date.desc())
            .limit(limit)
            .all()
        )

        if not interactions:
            return {
                "success": True,
                "hcp_name": hcp_name,
                "total_interactions": 0,
                "summary": f"No previous interactions found with {hcp_name}.",
                "interactions": []
            }

        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        all_topics = []
        all_materials = []

        interaction_list = []
        for i in interactions:
            s = (i.sentiment or "neutral").lower()
            if s in sentiment_counts:
                sentiment_counts[s] += 1
            if i.topics_discussed:
                all_topics.append(i.topics_discussed)
            if i.materials_shared:
                all_materials.append(i.materials_shared)
            interaction_list.append({
                "id": i.id,
                "date": i.date.strftime("%Y-%m-%d") if i.date else "Unknown",
                "type": i.interaction_type,
                "topics": i.topics_discussed,
                "sentiment": i.sentiment,
                "outcomes": i.outcomes,
            })

        dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        summary = (
            f"Interaction history with {hcp_name}: "
            f"{len(interactions)} total interaction(s). "
            f"Sentiment trend: {sentiment_counts['positive']} positive, "
            f"{sentiment_counts['neutral']} neutral, "
            f"{sentiment_counts['negative']} negative. "
            f"Overall relationship appears {dominant_sentiment}."
        )

        return {
            "success": True,
            "hcp_name": hcp_name,
            "total_interactions": len(interactions),
            "sentiment_breakdown": sentiment_counts,
            "dominant_sentiment": dominant_sentiment,
            "summary": summary,
            "interactions": interaction_list
        }
    except Exception as e:
        return {"error": str(e), "summary": ""}


# --- Build LangGraph Agent ---
TOOLS = [log_interaction, edit_interaction, search_hcp, suggest_follow_up, summarize_interaction_history]

SYSTEM_PROMPT = """You are an AI assistant embedded in a CRM system for pharmaceutical/life science field representatives.
Your role is to help sales reps log and manage their interactions with Healthcare Professionals (HCPs).

You have access to these tools:
1. log_interaction - Log a new HCP interaction (meetings, calls, emails)
2. edit_interaction - Edit/update an existing interaction by ID
3. search_hcp - Search for HCPs in the database
4. suggest_follow_up - Get follow-up action recommendations
5. summarize_interaction_history - Get history summary for an HCP

When a user describes an interaction (e.g., "Met Dr. Smith, discussed Product X, positive sentiment, shared brochure"),
ALWAYS use log_interaction tool to capture it.

Extract these details from natural language:
- HCP name (look for "Dr.", "Prof.", names)
- Interaction type (meeting/call/email/conference)
- Topics discussed
- Materials shared (brochures, samples, etc.)
- Sentiment (positive/neutral/negative based on context words)
- Outcomes and next steps

Be helpful, concise, and proactive. After logging, always offer follow-up suggestions."""


def create_agent(db: Session):
    set_db_session(db)

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=PRIMARY_MODEL,
        temperature=0.1,
    )
    llm_with_tools = llm.bind_tools(TOOLS)
    tool_node = ToolNode(TOOLS)

    def should_continue(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    def call_model(state: AgentState):
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()


def run_agent(message: str, conversation_history: list, db: Session) -> dict:
    """Run the LangGraph agent and return reply + any form updates."""
    agent = create_agent(db)

    messages = []
    for h in conversation_history:
        if h.get("role") == "user":
            messages.append(HumanMessage(content=h["content"]))
        elif h.get("role") == "assistant":
            messages.append(AIMessage(content=h["content"]))
    messages.append(HumanMessage(content=message))

    result = agent.invoke({
        "messages": messages,
        "form_updates": None,
        "action": None,
        "interaction_id": None,
        "db_session": db,
    })

    final_messages = result["messages"]
    reply_text = ""
    form_updates = None
    action = None
    interaction_id = None

    for msg in reversed(final_messages):
        if isinstance(msg, AIMessage) and msg.content:
            reply_text = msg.content
            break

    # Extract tool results for form updates
    for msg in final_messages:
        if isinstance(msg, ToolMessage):
            try:
                tool_result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                if isinstance(tool_result, dict):
                    if tool_result.get("form_updates"):
                        form_updates = tool_result["form_updates"]
                    if tool_result.get("interaction_id"):
                        interaction_id = tool_result["interaction_id"]
                    if tool_result.get("success"):
                        action = "logged" if "interaction_id" in tool_result else "updated"
            except (json.JSONDecodeError, TypeError):
                pass

    return {
        "reply": reply_text or "I processed your request.",
        "form_updates": form_updates,
        "action": action,
        "interaction_id": interaction_id,
    }
