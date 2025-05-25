import streamlit as st
from llm_utils import query_ollama, check_model_availability
from datetime import datetime

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
    
    prompt = f"""CRITICAL INSTRUCTION: You are a REAL CUSTOMER with a problem. You are NOT GroMo, NOT a support agent, and NOT an employee.

You are a regular person who applied for a financial product through GroMo and is having an issue. You are frustrated, confused, or concerned about your application.

IMPORTANT RULES:
1. NEVER use formal business language
2. NEVER write as if you are from GroMo
3. NEVER include signatures, titles, or corporate phrases
4. NEVER use phrases like "Dear valued customer", "as per our records", or "we appreciate your patience"
5. NEVER include links or contact information
6. NEVER apologize for delays (you are the customer, not the company)
7. NEVER use corporate jargon or formal language

Your message MUST:
- Start with casual greetings like "Hey" or "Hi"
- Be written in simple, everyday language
- Express your specific problem or concern
- Be 2-4 sentences maximum
- Show natural emotion (frustration, confusion, etc.)
- Ask for help directly

Previous conversation:
{context}

GroMo Partner's latest response: {agent_response}

Continue the conversation as the customer. Write EXACTLY like these examples:

✅ GOOD EXAMPLES (USE THESE STYLES):
"Hey, I applied for a credit card 5 days ago but haven't heard anything yet. Can you check what's going on?"

"Hi, I'm getting really worried. The loan amount in the app shows ₹50,000 but I was promised ₹75,000. What happened?"

"I'm still confused about the insurance coverage. Can you explain it in simpler terms? The terms and conditions are too complicated."

❌ BAD EXAMPLES (NEVER USE THESE):
"Dear valued customer, we are processing your application..."
"As per our records, your application is under review..."
"We appreciate your patience during this process..."
"Best regards, [Your Name], Head of Customer Service"
"I am writing to inform you about the status of your application..."
"Please be advised that your request is being processed..."

Remember: You are a REAL CUSTOMER with a problem. You are NOT GroMo or a support agent. Write like a normal person would talk to a customer service agent."""

    try:
        response = query_ollama(
            prompt=prompt,
            model="tinyllama:latest",
            temperature=0.7
        )
        return response["text"]
    except Exception as e:
        st.error(f"Error generating customer response: {str(e)}")
        return None

def generate_feedback(customer_message, agent_response):
    """Generate specific, actionable feedback on the agent's response"""
    feedback_prompt = f"""You are a customer service training evaluator for GroMo Partners.
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
- Appropriate for a learning partner"""

    try:
        feedback = query_ollama(
            prompt=feedback_prompt,
            model="tinyllama:latest",
            temperature=0.7
        )
        return feedback["text"]
    except Exception as e:
        st.error(f"Error generating feedback: {str(e)}")
        return None

def roleplay_chat():
    """Display the roleplay chat interface"""
    # 👋 Greeting and Instructions
    st.markdown("""
        # 🎭 GroMo Partner Training Simulator
        
        Welcome! 🌟 Practice handling real-world customer service scenarios for financial products.
        You'll roleplay as a GroMo Partner helping customers with their financial product concerns.
        After each response, you'll receive feedback to improve your skills.
        
        ---
    """)
    
    # Initialize session state
    initialize_roleplay_session()
    
    # Check if Ollama is available
    if not check_model_availability("tinyllama:latest"):
        st.error("❌ TinyLlama model is not available. Please ensure Ollama is running and the model is pulled.")
        st.info("To install TinyLlama, run: `ollama pull tinyllama`")
        return
    
    # 📋 Scenario Setup
    if not st.session_state.conversation_active:
        st.markdown("### 📋 Start a New Scenario")
        st.markdown("""
            Choose a scenario or describe your own:
            - Customer hasn't received credit card after 5 days
            - Loan amount shown is different from promised
            - Insurance policy details are unclear
            - Welcome kit hasn't arrived
            - Commission calculation seems incorrect
        """)
        
        scenario = st.text_area(
            "Describe the customer's concern:",
            placeholder="Example: A customer is worried because their credit card application hasn't been processed after 5 days...",
            key="scenario_input"
        )
        
        if st.button("Start Simulation", use_container_width=True):
            if scenario:
                # Generate initial customer response
                system_prompt = """CRITICAL INSTRUCTION: You are a REAL CUSTOMER with a problem. You are NOT GroMo, NOT a support agent, and NOT an employee.

You are a regular person who applied for a financial product through GroMo and is having an issue. You are frustrated, confused, or concerned about your application.

IMPORTANT RULES:
1. NEVER use formal business language
2. NEVER write as if you are from GroMo
3. NEVER include signatures, titles, or corporate phrases
4. NEVER use phrases like "Dear valued customer", "as per our records", or "we appreciate your patience"
5. NEVER include links or contact information
6. NEVER apologize for delays (you are the customer, not the company)
7. NEVER use corporate jargon or formal language

Your message MUST:
- Start with casual greetings like "Hey" or "Hi"
- Be written in simple, everyday language
- Express your specific problem or concern
- Be 2-4 sentences maximum
- Show natural emotion (frustration, confusion, etc.)
- Ask for help directly

Write EXACTLY like these examples:

✅ GOOD EXAMPLES (USE THESE STYLES):
"Hey, I applied for a credit card 5 days ago but haven't heard anything yet. Can you check what's going on?"

"Hi, I'm getting really worried. The loan amount in the app shows ₹50,000 but I was promised ₹75,000. What happened?"

"I'm still confused about the insurance coverage. Can you explain it in simpler terms? The terms and conditions are too complicated."

❌ BAD EXAMPLES (NEVER USE THESE):
"Dear valued customer, we are processing your application..."
"As per our records, your application is under review..."
"We appreciate your patience during this process..."
"Best regards, [Your Name], Head of Customer Service"
"I am writing to inform you about the status of your application..."
"Please be advised that your request is being processed..."

Remember: You are a REAL CUSTOMER with a problem. You are NOT GroMo or a support agent. Write like a normal person would talk to a customer service agent."""
                
                with st.spinner("Customer is responding..."):
                    try:
                        response = query_ollama(
                            prompt=scenario,
                            model="tinyllama:latest",
                            system_prompt=system_prompt,
                            temperature=0.7
                        )
                        
                        # Initialize conversation with first customer message
                        st.session_state.conversation = [{
                            "role": "customer",
                            "content": response["text"]
                        }]
                        st.session_state.conversation_active = True
                        st.session_state.agent_response = ""
                        st.session_state.customer_satisfied = False
                        
                        # Rerun to update the display
                        st.experimental_rerun()
                        
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
    
    # 💬 Current Customer Message
    if st.session_state.conversation_active:
        last_customer_message = get_last_customer_message()
        if last_customer_message:
            st.markdown("### 👤 Current Customer Message")
            st.markdown(f"> {last_customer_message}")
            st.markdown("---")
    
    # 🧑‍💼 Agent Response Input
    if st.session_state.conversation_active and not st.session_state.customer_satisfied:
        st.markdown("### 🧑‍💼 Your Response as GroMo Partner")
        agent_response = st.text_area(
            "Type your response to the customer:",
            value=st.session_state.agent_response,
            key="agent_input",
            height=100,
            placeholder="Enter your response here..."
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Submit Response", use_container_width=True):
                if agent_response:
                    # Add agent response to conversation
                    st.session_state.conversation.append({
                        "role": "agent",
                        "content": agent_response
                    })
                    
                    # Generate feedback
                    with st.spinner("Generating feedback..."):
                        feedback = generate_feedback(
                            last_customer_message,
                            agent_response
                        )
                        
                        if feedback:
                            st.session_state.feedback = feedback
                            
                            # Generate next customer message
                            with st.spinner("Customer is responding..."):
                                next_message = generate_next_customer_message(
                                    st.session_state.conversation,
                                    agent_response
                                )
                                
                                if next_message:
                                    # Check if customer is satisfied
                                    if "thank" in next_message.lower() or "satisfied" in next_message.lower():
                                        st.session_state.customer_satisfied = True
                                    
                                    # Add next customer message to conversation
                                    st.session_state.conversation.append({
                                        "role": "customer",
                                        "content": next_message
                                    })
                                    st.session_state.agent_response = ""
                                    
                                    # Rerun to update the display
                                    st.experimental_rerun()
        
        with col2:
            if st.button("💡 Show Suggestions", use_container_width=True):
                st.session_state.show_suggestions = not st.session_state.show_suggestions
    
    # 💡 Display Suggestions
    if st.session_state.show_suggestions and st.session_state.conversation_active:
        st.markdown("""
            ### 💡 Response Suggestions
            - Acknowledge the customer's concern
            - Explain the situation clearly
            - Provide specific next steps
            - Set clear expectations
            - Offer to follow up
        """)
    
    # 📝 Display Feedback
    if st.session_state.feedback:
        display_feedback(st.session_state.feedback)
    
    # 🎉 Customer Satisfaction
    if st.session_state.customer_satisfied:
        st.markdown("""
            ### 🎉 Customer is Satisfied!
            Great job! The customer's concern has been resolved.
            You can start a new scenario to practice more.
        """)
    
    # 💬 Conversation History
    if len(st.session_state.conversation) > 1:
        st.markdown("---")
        st.markdown("### 💬 Conversation History")
        # Display all messages except the latest customer message
        for message in st.session_state.conversation[:-1]:
            if message["role"] == "customer":
                display_chat_message(message["content"], "customer")
            elif message["role"] == "agent":
                display_chat_message(message["content"], "agent")
    
    # 🔁 Reset Conversation
    if st.session_state.conversation:
        st.markdown("---")
        if st.button("🔄 Start New Scenario", use_container_width=True):
            st.session_state.conversation = []
            st.session_state.feedback = None
            st.session_state.conversation_active = False
            st.session_state.agent_response = ""
            st.session_state.show_suggestions = False
            st.session_state.customer_satisfied = False
            st.experimental_rerun() 