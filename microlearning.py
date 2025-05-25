import streamlit as st
import json
from datetime import date, datetime
import random
from pathlib import Path
import pandas as pd

# Constants
CARDS_FILE = "assets/learning_cards.json"
PROGRESS_FILE = "assets/learning_progress.json"

def load_learning_cards():
    """Load learning cards from JSON file"""
    try:
        with open(CARDS_FILE, "r") as f:
            data = json.load(f)
            return data["cards"]
    except FileNotFoundError:
        st.error("Learning cards file not found!")
        return []
    except json.JSONDecodeError:
        st.error("Error reading learning cards file!")
        return []

def load_user_progress():
    """Load user's learning progress"""
    if 'learning_progress' not in st.session_state:
        try:
            with open(PROGRESS_FILE, "r") as f:
                st.session_state.learning_progress = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            st.session_state.learning_progress = {
                "completed_cards": [],
                "skill_progress": {},
                "last_card_date": None,
                "streak": 0
            }
    return st.session_state.learning_progress

def save_user_progress():
    """Save user's learning progress to file"""
    progress = st.session_state.learning_progress
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        st.error(f"Error saving progress: {str(e)}")

def get_daily_card(cards, progress):
    """Get today's learning card based on user progress and adaptive learning"""
    today = date.today().isoformat()
    
    # Check if we already have a card for today
    if progress["last_card_date"] == today:
        # Return the same card for today
        return next((card for card in cards if card["id"] == progress.get("today_card_id")), None)
    
    # Get user's skill progress
    skill_progress = progress["skill_progress"]
    
    # Find skills that need improvement (lowest progress)
    if skill_progress:
        min_progress_skill = min(skill_progress.items(), key=lambda x: x[1])[0]
        # Filter cards for that skill
        skill_cards = [card for card in cards if card["skill"] == min_progress_skill]
        if skill_cards:
            selected_card = random.choice(skill_cards)
        else:
            selected_card = random.choice(cards)
    else:
        # If no progress data, select randomly
        selected_card = random.choice(cards)
    
    # Update progress
    progress["last_card_date"] = today
    progress["today_card_id"] = selected_card["id"]
    save_user_progress()
    
    return selected_card

def update_skill_progress(card, completed=True):
    """Update progress for a specific skill"""
    progress = load_user_progress()
    skill = card["skill"]
    
    if skill not in progress["skill_progress"]:
        progress["skill_progress"][skill] = 0
    
    if completed:
        # Increase progress by 10% up to 100%
        progress["skill_progress"][skill] = min(100, progress["skill_progress"][skill] + 10)
    
    # Update completed cards
    if card["id"] not in progress["completed_cards"]:
        progress["completed_cards"].append(card["id"])
    
    save_user_progress()

def get_skill_progress_chart():
    """Create a progress chart for skills"""
    progress = load_user_progress()
    skill_progress = progress["skill_progress"]
    
    if not skill_progress:
        return None
    
    df = pd.DataFrame({
        'Skill': list(skill_progress.keys()),
        'Progress': list(skill_progress.values())
    })
    
    return df

def show_daily_card():
    """Display the daily learning card with interactive elements"""
    cards = load_learning_cards()
    if not cards:
        st.error("No learning cards available!")
        return
    
    progress = load_user_progress()
    card = get_daily_card(cards, progress)
    
    if not card:
        st.error("Error loading today's card!")
        return
    
    # Display card in a styled container
    st.markdown(f"""
        <div class="card">
            <h2>🎯 Today's Learning Focus: {card['title']}</h2>
            <p><strong>Skill Area:</strong> {card['skill']}</p>
            <p><strong>Difficulty:</strong> {card['difficulty']}</p>
            <hr>
            <div style='white-space: pre-line;'>{card['content']}</div>
            <hr>
            <p><strong>Tags:</strong> {', '.join(f'#{tag}' for tag in card['tags'])}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Completion button
    completed_key = f"completed_card_{card['id']}"
    if completed_key not in st.session_state:
        st.session_state[completed_key] = card["id"] in progress["completed_cards"]
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if not st.session_state[completed_key]:
            if st.button("✅ Mark as Completed", key=f"complete_{card['id']}"):
                st.session_state[completed_key] = True
                update_skill_progress(card, True)
                st.success("Great job! You've completed today's learning card!")
                st.rerun()
        else:
            st.success("✅ Completed!")
    
    # Show skill progress
    with st.expander("View Your Skill Progress"):
        df = get_skill_progress_chart()
        if df is not None:
            st.bar_chart(df.set_index('Skill'))
        else:
            st.info("Complete more cards to see your skill progress!")

def reset_progress():
    """Reset all learning progress"""
    if st.button("Reset All Progress", type="secondary"):
        st.session_state.learning_progress = {
            "completed_cards": [],
            "skill_progress": {},
            "last_card_date": None,
            "streak": 0
        }
        save_user_progress()
        st.success("Progress has been reset!")
        st.rerun()

if __name__ == "__main__":
    # Test the module
    st.title("Microlearning Module Test")
    show_daily_card()
    reset_progress() 