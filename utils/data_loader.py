import json
from pathlib import Path
import streamlit as st

def load_quiz_data(module_name: str):
    """Load quiz data for a specific module"""
    try:
        path = Path(__file__).parent.parent / 'assets' / 'data' / f"{module_name}_questions.json"
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get(module_name, [])
    except FileNotFoundError:
        st.error(f"Quiz data file not found for module: {module_name}")
        return []
    except json.JSONDecodeError:
        st.error(f"Error reading quiz data for module: {module_name}")
        return []

def save_user_progress(user_id: str, module_name: str, score: int):
    """Save user's quiz progress"""
    if 'quiz_progress' not in st.session_state:
        st.session_state.quiz_progress = {}
    
    if module_name not in st.session_state.quiz_progress:
        st.session_state.quiz_progress[module_name] = {}
    
    st.session_state.quiz_progress[module_name][user_id] = {
        'score': score,
        'timestamp': st.session_state.get('last_login')
    } 