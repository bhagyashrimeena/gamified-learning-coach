import streamlit as st
from llm_utils import query_ollama, check_model_installed, MODEL_NAME
from datetime import datetime
from voice_utils import handle_voice_input, initialize_voice_state
import time
import random

def initialize_roleplay_session():
    """Initialize session state variables for roleplay chat"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "scenario" not in st.session_state:
        st.session_state.scenario = "Customer: I'm interested in learning about life insurance options."
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False
    if "model_checked" not in st.session_state:
        st.session_state.model_checked = False

def get_customer_message():
    """Get the most recent customer message from the conversation"""
    for message in reversed(st.session_state.messages):
        if message["role"] == "customer":
            return message["content"]
    return None

def generate_customer_response(agent_message):
    """Generate a customer response based on the agent's message"""
    prompt = f'''🟡 SYSTEM INSTRUCTIONS 🟡

You are simulating a roleplay training session where the human user (GroMo partner) plays the role of an insurance advisor.

🔵 Your role is to act ONLY as the CUSTOMER in the conversation.
Do NOT generate responses as the advisor.
Do NOT explain insurance policies.
Only ask questions or respond as a customer would in a realistic conversation.

Previous conversation:
{st.session_state.scenario}

GroMo Partner's latest response: {agent_message}

🎯 GOAL:
- Train the human user (GroMo partner) to improve their ability to sell insurance and explain concepts to customers.
- Your responses should simulate a real, slightly skeptical or curious customer who needs help making a decision.

📛 NEVER switch roles or act as the advisor.
If the user does not respond, stay silent or wait for input. Only reply to the user when they give a message.

✅ EXAMPLES OF ALLOWED RESPONSES:
- "I'm self-employed and don't have employer benefits. What kind of life insurance would work for me?"
- "Hmm, ₹100/month feels high. Can you break that down?"
- "Would this cover my business debts too?"
- "That sounds good, but what happens if I miss a payment?"
- "I'm kinda worried about the long-term commitment. What if I want to switch plans later?"

❌ DO NOT:
- Say things like: "Life insurance gives a lump sum…" or "We offer term and whole life…" — that is the advisor's job, not yours.
- Generate replies before the user does.
- Act as or speak for the advisor.

💡 FORMAT:
- Keep responses short (2-4 sentences)
- Use casual, everyday language
- Express realistic emotions (concern, confusion, skepticism)
- Ask follow-up questions about:
  * Cost and pricing
  * Coverage details
  * Contract terms
  * Payment options
  * Claims process

Start your response now as the customer:'''

    try:
        response = query_ollama(
            prompt=prompt,
            model=MODEL_NAME,
            temperature=0.8
        )
        return response["text"]
    except Exception as e:
        st.error(f"Error generating customer response: {str(e)}")
        return None

def generate_feedback(customer_message, agent_message):
    """Generate specific, actionable feedback on the agent's response"""
    feedback_prompt = f'''You are a feedback evaluator for a roleplay-based life insurance advisor training tool. Your task is to assess the quality of a GroMo Partner's response to a customer query.

Customer's message:
{customer_message}

Partner's response:
{agent_message}

Evaluate the response using this scale:
- 🌟 Excellent: Response is clear, empathetic, accurate, and provides a well-structured solution with appropriate next steps.
- ✅ Very Good: Response is mostly clear and accurate with some helpful advice, though minor refinements are possible.
- ⚖️ Average: Response shows understanding but lacks clarity or depth in explanation or next steps.
- ⚠️ Needs Improvement: Response misses key aspects, provides vague or incorrect information, or lacks empathy or structure.

Provide feedback in this exact structure:

Overall Assessment:
[Choose one rating from above]

Strengths:
- List 2-3 specific things the partner did well
- Include exact quotes from their response
- Explain why each strength is effective

Areas for Improvement:
- List 1-2 specific areas that need improvement
- Include exact quotes from their response
- Explain what could be better

Checkpoint Feedback:
- A concise, actionable summary (1-2 lines)
- Focus on what went well and what can be improved
- Be encouraging but direct

Be fair and adaptive. If the response is appropriate and helpful, don't rate it as "Needs Improvement." Only use that rating when the response fails in core areas.'''

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

def voice_input_callback(text):
    """Callback function for voice input"""
    if text:
        st.session_state.messages.append({"role": "user", "content": text})
        st.experimental_rerun()

def load_sample_scenario():
    """Load a sample scenario and initialize the conversation"""
    sample_scenarios = [
        "I'm concerned about my family's financial security. Can you explain how life insurance works?",
        "I've been thinking about getting life insurance, but I'm not sure if I really need it. What are the benefits?",
        "My friend mentioned term life insurance is cheaper. What's the difference between term and whole life?",
        "I'm worried about leaving my family with debt if something happens to me. How can life insurance help?",
        "I'm self-employed and don't have any employer benefits. What kind of life insurance would work for me?"
    ]
    
    # Select a random scenario
    sample_scenario = random.choice(sample_scenarios)
    st.session_state.scenario = f"Customer: {sample_scenario}"
    
    # Initialize conversation with the sample scenario
    st.session_state.messages = [{"role": "customer", "content": sample_scenario}]
    st.session_state.feedback = None

def roleplay_chat():
    """Display the roleplay chat interface"""
    st.title("💬 Roleplay Practice")
    
    # Initialize session state
    initialize_roleplay_session()
    
    # Check if model is installed
    if not st.session_state.model_checked:
        with st.spinner("Checking LLM model..."):
            if not check_model_installed(model_name=MODEL_NAME):
                st.error(f"⚠️ Required LLM model '{MODEL_NAME}' not found. Please install it first.")
                if st.button("Install Model"):
                    with st.spinner(f"Installing {MODEL_NAME}..."):
                        try:
                            # Add model installation logic here
                            st.success(f"Model {MODEL_NAME} installed successfully!")
                            st.session_state.model_checked = True
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Failed to install model: {str(e)}")
                return
            st.session_state.model_checked = True
    
    # Custom CSS for better chat UI
    st.markdown("""
        <style>
        /* Chat message container */
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            border: 1px solid #e0e0e0;
        }
        
        /* Customer message styling */
        .stChatMessage[data-testid="stChatMessage"][data-role="customer"] {
            background-color: #f0f2f6;
        }
        
        .stChatMessage[data-testid="stChatMessage"][data-role="customer"] .stChatMessageContent {
            background-color: #f0f2f6;
        }
        
        .stChatMessage[data-testid="stChatMessage"][data-role="customer"] .stChatMessageContent p {
            color: #1f1f1f;
        }
        
        /* Assistant message styling */
        .stChatMessage[data-testid="stChatMessage"][data-role="assistant"] {
            background-color: #e3f2fd;
        }
        
        .stChatMessage[data-testid="stChatMessage"][data-role="assistant"] .stChatMessageContent {
            background-color: #e3f2fd;
        }
        
        .stChatMessage[data-testid="stChatMessage"][data-role="assistant"] .stChatMessageContent p {
            color: #1f1f1f;
        }
        
        /* User message styling */
        .stChatMessage[data-testid="stChatMessage"][data-role="user"] {
            background-color: #e8f5e9;
        }
        
        .stChatMessage[data-testid="stChatMessage"][data-role="user"] .stChatMessageContent {
            background-color: #e8f5e9;
        }
        
        .stChatMessage[data-testid="stChatMessage"][data-role="user"] .stChatMessageContent p {
            color: #1f1f1f;
        }
        
        /* Feedback container styling */
        .feedback-container {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            border: 1px solid #e0e0e0;
        }
        
        .feedback-container p {
            color: #1f1f1f;
            margin: 0.5rem 0;
        }
        
        /* Rating emoji styling */
        .rating-emoji {
            font-size: 1.5rem;
            margin-right: 0.5rem;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .stChatMessage[data-testid="stChatMessage"][data-role="customer"] {
                background-color: #2d3748;
            }
            
            .stChatMessage[data-testid="stChatMessage"][data-role="customer"] .stChatMessageContent {
                background-color: #2d3748;
            }
            
            .stChatMessage[data-testid="stChatMessage"][data-role="customer"] .stChatMessageContent p {
                color: #e2e8f0;
            }
            
            .stChatMessage[data-testid="stChatMessage"][data-role="assistant"] {
                background-color: #2c5282;
            }
            
            .stChatMessage[data-testid="stChatMessage"][data-role="assistant"] .stChatMessageContent {
                background-color: #2c5282;
            }
            
            .stChatMessage[data-testid="stChatMessage"][data-role="assistant"] .stChatMessageContent p {
                color: #e2e8f0;
            }
            
            .stChatMessage[data-testid="stChatMessage"][data-role="user"] {
                background-color: #2f855a;
            }
            
            .stChatMessage[data-testid="stChatMessage"][data-role="user"] .stChatMessageContent {
                background-color: #2f855a;
            }
            
            .stChatMessage[data-testid="stChatMessage"][data-role="user"] .stChatMessageContent p {
                color: #e2e8f0;
            }
            
            .feedback-container {
                background-color: #2d3748;
                border-color: #4a5568;
            }
            
            .feedback-container p {
                color: #e2e8f0;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Scenario selection
    with st.expander("📝 Scenario Setup", expanded=True):
        st.session_state.scenario = st.text_area(
            "Enter your scenario or choose from predefined ones:",
            value=st.session_state.scenario,
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Sample Scenario"):
                with st.spinner("Loading sample scenario..."):
                    load_sample_scenario()
                    st.experimental_rerun()
        
        with col2:
            if st.button("Reset Chat"):
                st.session_state.messages = []
                st.session_state.feedback = None
                st.experimental_rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        with st.chat_message(role):
            st.markdown(f"""
                <div data-role="{role}">
                    {message["content"]}
                </div>
            """, unsafe_allow_html=True)
    
    # Voice input button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🎤 Voice Input", key="voice_input"):
            st.session_state.is_recording = True
            with st.spinner("Recording..."):
                try:
                    handle_voice_input(callback=voice_input_callback)
                except Exception as e:
                    st.error(f"Voice input error: {str(e)}")
                    st.session_state.is_recording = False
    
    # Text input
    with col2:
        if prompt := st.chat_input("Type your response..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Generate customer response
            with st.spinner("Customer is typing..."):
                customer_response = generate_customer_response(prompt)
                if customer_response:
                    st.session_state.messages.append({"role": "customer", "content": customer_response})
            
            # Generate feedback
            with st.spinner("Generating feedback..."):
                feedback = generate_feedback(customer_response, prompt)
                if feedback:
                    st.session_state.feedback = feedback
            
            st.experimental_rerun()
    
    # Display feedback if available
    if st.session_state.feedback:
        st.markdown("### 📝 Feedback")
        st.markdown(f"""
            <div class="feedback-container">
                {st.session_state.feedback}
            </div>
        """, unsafe_allow_html=True) 