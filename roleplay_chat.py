import streamlit as st
from llm_utils import query_ollama, check_model_installed, MODEL_NAME
from datetime import datetime
from voice_utils import handle_voice_input, initialize_voice_state

def initialize_roleplay_session():
    """Initialize session state variables for roleplay chat"""
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "conversation_active" not in st.session_state:
        st.session_state.conversation_active = False
    if "agent_response" not in st.session_state:
        st.session_state.agent_response = ""
    if "show_suggestions" not in st.session_state:
        st.session_state.show_suggestions = False
    if "customer_satisfied" not in st.session_state:
        st.session_state.customer_satisfied = False
    if "scenario_input" not in st.session_state:
        st.session_state.scenario_input = ""
    if "agent_input" not in st.session_state:
        st.session_state.agent_input = ""
    if "reset_requested" not in st.session_state:
        st.session_state.reset_requested = False

def get_last_customer_message():
    """Get the most recent customer message from the conversation"""
    for message in reversed(st.session_state.conversation):
        if message["role"] == "customer":
            return message["content"]
    return None

def display_chat_message(message, role):
    """Display a chat message with appropriate styling"""
    timestamp = datetime.now().strftime("%H:%M")
    
    if role == "customer":
        st.markdown(f"""
            <div style='display: flex; margin-bottom: 1rem;'>
                <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 1rem; max-width: 80%;'>
                    <div style='color: #666; font-size: 0.8rem; margin-bottom: 0.5rem;'>👤 Customer • {timestamp}</div>
                    <div style='color: #1f1f1f;'>{message}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif role == "agent":
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-end; margin-bottom: 1rem;'>
                <div style='background-color: #e3f2fd; padding: 1rem; border-radius: 1rem; max-width: 80%;'>
                    <div style='color: #666; font-size: 0.8rem; margin-bottom: 0.5rem;'>🧑‍💼 You (GroMo Partner) • {timestamp}</div>
                    <div style='color: #1f1f1f;'>{message}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def display_feedback(feedback):
    """Display feedback in a structured format"""
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0;'>
            <h3 style='color: #1f1f1f; margin-bottom: 1rem;'>🧠 Feedback on Your Response</h3>
    """, unsafe_allow_html=True)
    
    # Split feedback into sections
    sections = feedback.split('\n\n')
    for section in sections:
        if section.strip():
            st.markdown(f"<div style='margin-bottom: 1rem;'>{section}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def generate_next_customer_message(conversation, agent_response):
    """Generate the next customer message based on conversation context"""
    # Build conversation context from last 2 exchanges
    context = "Previous conversation:\n"
    for msg in conversation[-4:]:  # Last 2 exchanges (4 messages)
        if msg["role"] == "customer":
            context += f"Customer: {msg['content']}\n"
        elif msg["role"] == "agent":
            context += f"GroMo Partner: {msg['content']}\n"
    
    prompt = f'''You are a real customer, not a bot or a support agent.

You are speaking casually about a real problem you are facing related to a financial product (credit card, loan, insurance etc).

Previous conversation:
{context}

GroMo Partner's latest response: {agent_response}

CRITICAL INSTRUCTIONS:
• Speak casually and simply
• Do not use any formal or business language
• Never act like GroMo or an agent
• Show mild frustration, confusion, or concern
• Use real-life language like: "hey", "hi", "what's going on?", "this is so annoying", etc.
• Write only 2-4 lines MAXIMUM

Start now:'''

    try:
        response = query_ollama(
            prompt=prompt,
            model=MODEL_NAME,
            temperature=0.7
        )
        return response["text"]
    except Exception as e:
        st.error(f"Error generating customer response: {str(e)}")
        return None

def generate_feedback(customer_message, agent_response):
    """Generate specific, actionable feedback on the agent's response"""
    feedback_prompt = f'''You are a customer service training evaluator for GroMo Partners.
Evaluate the partner's response to the customer's message about financial products.
Provide specific, actionable feedback that helps the partner improve their skills.

Customer's message:
{customer_message}

Partner's response:
{agent_response}

Evaluate the response based on these criteria:
1. Empathy and Tone: Is the response empathetic and respectful?
2. Clarity and Accuracy: Does it explain the situation clearly and correctly?
3. Action Orientation: Does it provide clear next steps or solutions?
4. Product Knowledge: Does it demonstrate understanding of financial products?
5. Customer Focus: Does it address the customer's specific concern?

Provide feedback in this exact structure:

Overall Assessment:
- Start with ✅ "Good response!" if effective, or ⚠️ "Needs improvement" if weak
- Briefly explain the key strength or area needing improvement

Strengths:
- List 2 specific things the partner did well
- Include exact quotes from their response
- Explain why each strength is effective for financial product support

Areas for Improvement:
- List 2 specific areas that need improvement
- Include exact quotes from their response
- Explain what could be better

Suggestions for Better Response:
- Provide 2-3 specific example phrases the partner could use
- Include better ways to explain financial concepts
- Show how to handle the situation more effectively

Keep the feedback:
- Constructive and supportive
- Specific to financial product support
- Focused on practical improvements
- Clear and actionable
- Appropriate for a learning partner'''

    try:
        feedback = query_ollama(
            prompt=feedback_prompt,
            model=MODEL_NAME,
            temperature=0.7
        )
        return feedback["text"]
    except Exception as e:
        st.error(f"Error generating feedback: {str(e)}")
        return None

def roleplay_chat():
    """Display the roleplay chat interface"""
    st.header("💬 Roleplay Practice")
    
    # Initialize chat history in session state if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Scenario selection
    with st.expander("Select a Scenario", expanded=True):
        scenario = st.text_area(
            "Enter your scenario or choose from predefined ones:",
            value="Customer: I'm interested in learning about life insurance options.",
            height=100
        )
        
        # Add predefined scenarios
        if st.button("Load Sample Scenario"):
            scenario = "Customer: I'm concerned about my family's financial security. Can you explain how life insurance works?"
            st.experimental_rerun()

    # Chat interface
    st.markdown("### Chat Interface")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input
    if prompt := st.chat_input("Type your response..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Simulate AI response (replace with actual AI response later)
        ai_response = "I understand you're interested in life insurance. Let me explain the different types of policies available..."
        
        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Display AI response
        with st.chat_message("assistant"):
            st.write(ai_response)

    # Add a reset button
    if st.button("Reset Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun() 