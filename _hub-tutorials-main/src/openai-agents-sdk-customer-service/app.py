import streamlit as st
import asyncio
from agents import Runner, Agent, ItemHelpers, RunContextWrapper, function_tool
from agents.extensions.models.litellm_model import LitellmModel
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv(".env")

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Airline Customer Service",
    page_icon="✈️",
    layout="wide"
)

# --- CONTEXT ---
class AirlineAgentContext(BaseModel):
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None

# --- TOOLS ---
@function_tool(
    name_override="faq_lookup_tool",
    description_override="Lookup frequently asked questions."
)
async def faq_lookup_tool(question: str) -> str:
    question_lower = question.lower()
    if any(kw in question_lower for kw in ["bag", "baggage", "luggage", "carry-on"]):
        return (
            "You are allowed to bring one bag on the plane. "
            "It must be under 50 pounds and 22 inches x 14 inches x 9 inches."
        )
    elif any(kw in question_lower for kw in ["seat", "seats", "seating"]):
        return (
            "There are 120 seats on the plane. "
            "22 business class, 98 economy. Exit rows: 4 and 16. "
            "Rows 5-8 are Economy Plus with extra legroom."
        )
    elif any(kw in question_lower for kw in ["wifi", "internet", "wireless"]):
        return "We have free wifi on the plane, join Airline-Wifi"
    return "I'm sorry, I don't know the answer to that question."


@function_tool
async def update_seat(
    ctx: RunContextWrapper[AirlineAgentContext],
    confirmation_number: str,
    new_seat: str
) -> str:
    """Update the seat for a given confirmation number."""
    ctx.context.confirmation_number = confirmation_number
    ctx.context.seat_number = new_seat
    return f"Updated seat to {new_seat} for confirmation number {confirmation_number}"


# --- AGENTS ---
def create_agents():
    if "agents" in st.session_state:
        return st.session_state.agents

    api_key = os.environ.get("HF_TOKEN") or st.secrets.get("HF_TOKEN")
    model = LitellmModel(
        model="huggingface/nscale/Qwen/Qwen3-8B",
        api_key=api_key,
    )

    faq_agent = Agent[AirlineAgentContext](
        name="FAQ Agent",
        handoff_description="A helpful agent that can answer questions about the airline.",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
        You are an FAQ agent. Use the following routine:
        1. Identify the last question asked by the customer.
        2. Use the faq lookup tool to answer. Do not rely on your own knowledge.
        3. If you cannot answer, transfer back to the triage agent.""",
        tools=[faq_lookup_tool],
        model=model,
    )

    seat_booking_agent = Agent[AirlineAgentContext](
        name="Seat Booking Agent",
        handoff_description="A helpful agent that can update a seat on a flight.",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
        You are a seat booking agent. Use the following routine:
        1. Ask for their confirmation number.
        2. Ask the customer what their desired seat number is.
        3. Use the update seat tool to update the seat.
        If unrelated question, transfer back to triage agent.""",
        tools=[update_seat],
        model=model,
    )

    triage_agent = Agent[AirlineAgentContext](
        name="Triage Agent",
        handoff_description="A triage agent that delegates requests to appropriate agents.",
        instructions=(
            f"{RECOMMENDED_PROMPT_PREFIX} "
            "You are a helpful triaging agent. Delegate questions to other appropriate agents."
        ),
        handoffs=[faq_agent, seat_booking_agent],
        model=model,
    )

    faq_agent.handoffs.append(triage_agent)
    seat_booking_agent.handoffs.append(triage_agent)

    st.session_state.agents = (triage_agent, faq_agent, seat_booking_agent)
    return st.session_state.agents


# --- INIT STATE ---
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_context" not in st.session_state:
        st.session_state.agent_context = AirlineAgentContext(
            flight_number="FLT-123",
            seat_number="A12",
            passenger_name="John Doe",
        )
    if "current_agent" not in st.session_state:
        triage, _, _ = create_agents()
        st.session_state.current_agent = triage
    if "events" not in st.session_state:
        st.session_state.events = []


# --- RUN AGENT ---
async def run_agent(user_input: str):
    triage, _, _ = create_agents()

    # Build conversation history
    input_items = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            input_items.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant":
            input_items.append({"role": "assistant", "content": msg["content"]})

    # Add current user message
    input_items.append({"role": "user", "content": user_input})

    # Run the agent
    result = await Runner.run(
        starting_agent=st.session_state.current_agent,
        input=input_items,
        context=st.session_state.agent_context,
    )

    # Process events for UI
    events = []
    for item in result.new_items:
        if item.type == "handoff_output_item":
            events.append({
                "type": "handoff",
                "from": item.source_agent.name if hasattr(item, 'source_agent') and item.source_agent else "Unknown",
                "to": item.target_agent.name if hasattr(item, 'target_agent') and item.target_agent else "Unknown",
            })
        elif item.type == "tool_call_item":
            events.append({
                "type": "tool_call",
                "tool": item.raw_item.name if hasattr(item.raw_item, 'name') else str(item.raw_item),
            })
        elif item.type == "tool_call_output_item":
            events.append({
                "type": "tool_output",
                "output": item.output[:100] + "..." if len(item.output) > 100 else item.output,
            })

    # Update state
    st.session_state.current_agent = result.last_agent
    # Context is mutated in-place by tools, no need to reassign
    st.session_state.events = events

    # Get final response
    response = ItemHelpers.text_message_outputs(result.new_items)
    return response


# --- UI ---
def main():
    init_state()

    st.title("✈️ Airline Customer Service")
    st.caption("Multi-agent system demo with OpenAI Agents SDK")

    # Sidebar: Agent status and events
    with st.sidebar:
        st.header("Agent Status")
        current = st.session_state.current_agent
        st.metric("Current Agent", current.name if current else "None")

        st.divider()
        st.header("Context")
        ctx = st.session_state.agent_context
        st.json({
            "passenger": ctx.passenger_name,
            "flight": ctx.flight_number,
            "seat": ctx.seat_number,
            "confirmation": ctx.confirmation_number,
        })

        st.divider()
        st.header("Last Turn Events")
        if st.session_state.events:
            for event in st.session_state.events:
                if event["type"] == "handoff":
                    st.info(f"🔄 Handoff: {event['from']} → {event['to']}")
                elif event["type"] == "tool_call":
                    st.warning(f"🔧 Tool: {event['tool']}")
                elif event["type"] == "tool_output":
                    st.success(f"📤 Output: {event['output']}")
        else:
            st.caption("No events yet")

        if st.button("Reset Conversation"):
            st.session_state.messages = []
            st.session_state.events = []
            st.session_state.pop("agents", None)
            triage, _, _ = create_agents()
            st.session_state.current_agent = triage
            st.session_state.agent_context = AirlineAgentContext(
                flight_number="FLT-123",
                seat_number="A12",
                passenger_name="John Doe",
            )
            st.rerun()

    # Chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about baggage, seats, WiFi, or book a seat..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = asyncio.run(run_agent(prompt))
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


if __name__ == "__main__":
    main()
