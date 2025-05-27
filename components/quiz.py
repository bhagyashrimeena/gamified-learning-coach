import streamlit as st
from utils.data_loader import save_user_progress
from utils.question_generator import generate_questions

def show_quiz(module_name: str):
    """Display a quiz for the specified module"""
    st.markdown("### 📝 Quiz: Insurance Basics")
    
    # Initialize session state for quiz
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    
    # Load quiz questions (now generated dynamically)
    # We pass 'Insurance Fundamentals' as the topic to the generator for this module
    questions = generate_questions("Insurance Fundamentals")
    
    if not questions:
        st.error("No questions available for this module.")
        return
    
    # Display questions
    for idx, q in enumerate(questions, start=1):
        st.markdown(f"**Q{idx}.** {q['question']}")
        
        # Create a unique key for each question
        question_key = f"quiz_{module_name}_{idx}"
        
        # Display options
        if question_key not in st.session_state.quiz_answers:
            st.session_state.quiz_answers[question_key] = None
        
        choice = st.radio(
            f"Select an answer for Q{idx}",
            q['options'],
            key=question_key,
            disabled=st.session_state.quiz_submitted
        )
        
        # Show feedback if quiz is submitted
        if st.session_state.quiz_submitted:
            if choice == q['answer']:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. The correct answer is: {q['answer']}")
                st.info(f"Explanation: {q['explanation']}")
    
    # Submit button
    if not st.session_state.quiz_submitted:
        if st.button("Submit Quiz", type="primary"):
            # Calculate score
            score = sum(1 for idx, q in enumerate(questions, start=1)
                       if st.session_state.quiz_answers[f"quiz_{module_name}_{idx}"] == q['answer'])
            
            # Save progress
            if st.session_state.get('user_name'):
                save_user_progress(st.session_state.user_name, module_name, score)
            
            # Update session state
            st.session_state.quiz_submitted = True
            st.session_state.quiz_score = score
            
            # Show score
            st.success(f"🎉 Your Score: {score} / {len(questions)}")
            
            # Add XP for completing quiz
            if 'user_xp' in st.session_state:
                st.session_state.user_xp += score * 10  # 10 XP per correct answer
            
            st.rerun()
    else:
        # Reset button
        if st.button("Try Again"):
            st.session_state.quiz_submitted = False
            st.session_state.quiz_answers = {}
            st.rerun() 