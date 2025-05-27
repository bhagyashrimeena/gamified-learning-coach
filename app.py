import streamlit as st
import datetime
from pathlib import Path
import json
import plotly.express as px
import pandas as pd
from microlearning import show_daily_card, reset_progress
from roleplay_chat import roleplay_chat
import os

# Set page configuration
st.set_page_config(
    page_title="AI Learning Coach",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme configuration
st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .card {
        background-color: #2D2D2D;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize main session state variables
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'streak_count' not in st.session_state:
    st.session_state.streak_count = 0
if 'last_login' not in st.session_state:
    st.session_state.last_login = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_xp' not in st.session_state:
    st.session_state.user_xp = 0

def get_greeting():
    """Return appropriate greeting based on time of day"""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def update_streak():
    """Update user's login streak"""
    today = datetime.datetime.now().date()
    if st.session_state.last_login:
        last_login = datetime.datetime.fromisoformat(st.session_state.last_login).date()
        if (today - last_login).days == 1:
            st.session_state.streak_count += 1
        elif (today - last_login).days > 1:
            st.session_state.streak_count = 1
    else:
        st.session_state.streak_count = 1
    st.session_state.last_login = today.isoformat()

def load_css():
    """Load custom CSS for styling"""
    css_file = os.path.join("assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_dashboard():
    """Display the main dashboard with progress metrics"""
    st.header("Your Learning Dashboard 📊")
    
    # Placeholder for actual metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Skills Mastered", "3/10")
    with col2:
        st.metric("Practice Sessions", "12")
    with col3:
        st.metric("Average Score", "85%")
    
    # Placeholder for progress chart
    st.subheader("Skill Progress")
    data = pd.DataFrame({
        'Skill': ['Active Listening', 'Empathy', 'Problem Solving', 'Communication'],
        'Progress': [75, 85, 60, 90]
    })
    fig = px.line(data, x='Skill', y='Progress', title='Skill Development Over Time')
    st.plotly_chart(fig)

def show_daily_learning():
    """Display the daily learning card and related features"""
    st.header("📚 Daily Learning")
    
    # Show the daily card
    show_daily_card()
    
    # Add a reset progress button in a less prominent location
    with st.sidebar:
        st.markdown("---")
        with st.expander("Advanced Options"):
            reset_progress()

def show_roleplay():
    """Display the roleplay chat interface"""
    roleplay_chat()

def show_voice_analysis():
    """Display the voice analysis interface"""
    st.header("🎤 Voice Analysis")
    st.markdown("Practice your speaking skills and get real-time feedback.")
    # Placeholder for voice analysis
    st.button("Start Recording")

def show_achievements():
    """Display user achievements and badges"""
    st.header("🏆 Your Achievements")
    # Placeholder for achievements
    st.markdown("""
        <div class="card">
            <h3>🎯 First Steps</h3>
            <p>Completed your first learning session</p>
        </div>
        <div class="card">
            <h3>🔥 Streak Master</h3>
            <p>Maintained a 7-day learning streak</p>
        </div>
    """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    # Load custom CSS
    load_css()

    # Update streak
    update_streak()

    # Sidebar
    with st.sidebar:
        st.title("🤖 AI Learning Coach")

        if not st.session_state.user_name:
            st.session_state.user_name = st.text_input("Enter your name to begin")
            if st.session_state.user_name:
                update_streak()

        if st.session_state.user_name:
            st.write(f"Welcome back, {st.session_state.user_name}! 👋")
            st.write(f"🔥 Current streak: {st.session_state.streak_count} days")

            st.markdown("---")
            st.markdown("### Navigation")
            page = st.radio(
                "Choose a section:",
                ["🏠 Dashboard", "📚 Daily Learning", "💬 Roleplay Practice",
                 "🎤 Voice Analysis", "🏆 Achievements"]
            )

    # Main content area
    if not st.session_state.user_name:
        st.title("Welcome to AI Learning Coach! 🎓")
        st.markdown("""
            Please enter your name in the sidebar to begin your learning journey.
            This AI-powered platform will help you improve your customer service skills
            through daily practice and personalized feedback.
        """)
        return

    # Display greeting
    greeting = get_greeting()
    st.title(f"{greeting}, {st.session_state.user_name}! 🌟")

    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📚 Daily Learning":
        show_daily_learning()
    elif page == "💬 Roleplay Practice":
        show_roleplay()
    elif page == "🎤 Voice Analysis":
        show_voice_analysis()
    elif page == "🏆 Achievements":
        show_achievements()

    # Update streak at the end of the session
    update_streak()

if __name__ == "__main__":
    main() 