import streamlit as st
import json # Need json for load_module_data if it were loading from file, but it's defined here now
# Removed: from utils.data_loader import save_user_progress # This might not be used anymore after refactoring quiz
from utils.question_generator import generate_questions
# Removed: from pages.course_module_ui import initialize_completion_state, render_progress_bar, render_section

# The following functions are moved into this file from the deleted course_module_ui.py
# Initialize section completion state (used in app.py now)
def initialize_section_completion_state(sections):
    """Initialize session state for tracking section completion."""
    if 'section_completion_status' not in st.session_state:
        st.session_state.section_completion_status = {}
    # Ensure state is initialized for each section
    for section in sections:
        if section not in st.session_state.section_completion_status:
            st.session_state.section_completion_status[section] = False

# Render progress bar (moved to app.py now)
def render_section_progress_bar(sections):
    """Render the dynamic progress bar based on completed sections."""
    total_sections = len(sections)
    completed_sections = sum(1 for section, completed in st.session_state.section_completion_status.items() if completed)

    st.markdown("### Module Progress")
    progress_percentage = (completed_sections / total_sections) if total_sections > 0 else 0
    st.progress(progress_percentage, text=f"{completed_sections}/{total_sections} sections completed")

# Simplified render_section (content rendering is manual now)
def render_content_for_section(section_name, items):
     """Display content for a section (no checkboxes here)."""
     # The actual content rendering logic is inside show_insurance_module based on selected_section
     pass

# Initialize item and section completion state
def initialize_all_completion_states(module_data):
    """Initialize session state for tracking item and section completion."""
    if 'item_completion_status' not in st.session_state:
        st.session_state.item_completion_status = {}
        # Initialize state for each item
        for section, items in module_data.items():
            for i, item in enumerate(items):
                item_key = f"{section.lower().replace(' ', '_')}_{i}"
                if item_key not in st.session_state.item_completion_status:
                    st.session_state.item_completion_status[item_key] = False

    if 'section_completion_status' not in st.session_state:
        st.session_state.section_completion_status = {}
        # Initialize state for each section
        for section in module_data.keys():
            if section not in st.session_state.section_completion_status:
                st.session_state.section_completion_status[section] = False

# Render progress bar for items within a section
def render_section_item_progress_bar(section_name, items):
    """Render the dynamic progress bar based on completed items within a section."""
    total_items = len(items)
    if 'item_completion_status' not in st.session_state:
        st.session_state.item_completion_status = {}

    completed_items = sum(1 for i, item in enumerate(items)
                         if st.session_state.item_completion_status.get(f"{section_name.lower().replace(' ', '_')}_{i}", False))

    st.markdown("#### Section Progress")
    progress_percentage = (completed_items / total_items) if total_items > 0 else 0
    st.progress(progress_percentage, text=f"{completed_items}/{total_items} items completed in this section")

# Render progress bar for completed sections (used in app.py)
def render_module_section_progress_bar(sections):
    """Render the dynamic progress bar based on completed sections for the module."""
    total_sections = len(sections)
    # Ensure section_completion_status exists in session state
    if 'section_completion_status' not in st.session_state:
        st.session_state.section_completion_status = {}

    completed_sections = sum(1 for section, completed in st.session_state.section_completion_status.items() if completed)

    st.markdown("### Module Progress")
    progress_percentage = (completed_sections / total_sections) if total_sections > 0 else 0
    st.progress(progress_percentage, text=f"{completed_sections}/{total_sections} sections completed")

def load_insurance_module_data():
    """Define the content structure for the Insurance Basics module."""
    # This structure is used for defining sections, their order, and individual items
    module_content = {
        "Readings": [
            {"title": "Module Description and Learning Objectives", "duration": "~5 min"},
            {"title": "1. What is Insurance?", "duration": "~5 min"},
            {"title": "2. Types of Insurance", "duration": "~10 min"},
            {"title": "3. Key Insurance Principles", "duration": "~10 min"},
        ],
        "Quizzes": [
            {"title": "Test Your Knowledge: Insurance Basics", "duration": "~10 min"},
        ],
        "Resources": [
            {"title": "Additional Resources", "duration": "~5 min"},
        ]
    }
    return module_content

def render_quiz_section():
    """Render the quiz content specifically for the insurance module."""
    st.markdown("#### Test Your Knowledge: Insurance Basics")
    st.markdown("Take this quiz to test your understanding of insurance basics!")

    module_name = "module1"
    questions = generate_questions("Insurance Fundamentals")

    if not questions:
        st.error("No questions available for this module.")
        return

    quiz_state_key = f'quiz_state_{module_name}'
    if quiz_state_key not in st.session_state:
        st.session_state[quiz_state_key] = {
            'submitted': False,
            'answers': {}
        }

    quiz_state = st.session_state[quiz_state_key]

    # Track attempted questions for progress bar
    attempted_questions = sum(1 for answer in quiz_state['answers'].values() if answer is not None)
    total_questions = len(questions)
    quiz_progress_percentage = (attempted_questions / total_questions) if total_questions > 0 else 0
    st.progress(quiz_progress_percentage, text=f"{attempted_questions}/{total_questions} questions attempted")

    for idx, q in enumerate(questions, start=1):
        st.markdown(f"**Q{idx}.** {q['question']}")
        question_key = f"{module_name}_{idx}"

        if question_key not in quiz_state['answers']:
            quiz_state['answers'][question_key] = None

        choice = st.radio(
            f"Select an answer for Q{idx}",
            q['options'],
            key=f'radio_{module_name}_{idx}',
            index=q['options'].index(quiz_state['answers'][question_key]) if quiz_state['answers'][question_key] in q['options'] else None,
            disabled=quiz_state['submitted']
        )

        if choice != quiz_state['answers'].get(question_key):
            quiz_state['answers'][question_key] = choice

        if quiz_state['submitted']:
            if choice == q['answer']:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. The correct answer is: {q['answer']}")
                st.info(f"Explanation: {q['explanation']}")

    if not quiz_state['submitted']:
        if st.button("Submit Quiz", type="primary", key=f'submit_{module_name}'):
            score = sum(1 for idx, q in enumerate(questions, start=1)
                       if quiz_state['answers'].get(f"{module_name}_{idx}") == q['answer'])

            quiz_state['submitted'] = True
            quiz_state['score'] = score

            st.success(f"🎉 Your Score: {score} / {len(questions)}")
            st.experimental_rerun()

    else:
        st.info(f"Your Score: {quiz_state.get('score', 0)} / {len(questions)}")
        if st.button("Try Again", key=f'try_again_{module_name}'):
            st.session_state[quiz_state_key] = {
                'submitted': False,
                'answers': {}
            }
            st.experimental_rerun()

def show_insurance_module():
    """Display the insurance module content with Coursera-style UI and sidebar navigation."""
    st.title("🏥 Insurance Module") # Changed title to be more specific

    module_data = load_insurance_module_data()
    sections = list(module_data.keys())

    # Sidebar navigation for sections within the module
    with st.sidebar:
        st.title("🤖 AI Learning Coach")
        st.markdown("### 📖 Learn")
        st.markdown("#### Learning Module:")
        st.markdown("🔴 Insurance Module")
        
        st.markdown("#### Module Progress")
        render_module_section_progress_bar(sections)

        st.markdown("---")
        st.markdown("### Module 1")
        # Use expander for the module sections
        with st.expander("Sections", expanded=True):
            # Use session state to keep track of the selected section within the module
            if 'selected_insurance_section_internal' not in st.session_state:
                st.session_state.selected_insurance_section_internal = sections[0]

            selected_section = st.radio(
                "", # Removed "Go to" label
                sections,
                key="insurance_module_section_nav_internal"
            )

            # Update session state if a different section is selected
            if selected_section != st.session_state.selected_insurance_section_internal:
                st.session_state.selected_insurance_section_internal = selected_section
                st.experimental_rerun()

    # Get the selected section from session state for rendering
    current_section = st.session_state.get('selected_insurance_section_internal', sections[0])

    # Main content area based on selected section
    if current_section == "Readings":
        st.markdown("### 📖 Reading Materials")

        # Content for readings section
        st.markdown("""
        Welcome to the Insurance Basics module! This module will help you understand:
        - The fundamental concepts of insurance
        - Different types of insurance
        - Key insurance principles
        - Common insurance terms and their meanings.
        """)
        
        with st.expander("📚 Learning Objectives"):
            st.markdown("""
            By the end of this module, you will be able to:
            1. Explain the basic purpose and function of insurance
            2. Identify different types of insurance products
            3. Understand key insurance principles
            4. Apply insurance concepts in real-world scenarios.
            """)

        st.markdown("#### 1. What is Insurance?")
        st.markdown("""
        Insurance is a contract between an individual (the insured) and an insurance company (the insurer),
        where the insurer agrees to provide financial protection against specific risks in exchange for regular payments (premiums).
        """)

        st.markdown("#### 2. Types of Insurance")
        st.markdown("""
        There are several types of insurance, including:
        - Life Insurance
        - Health Insurance
        - Auto Insurance
        - Property Insurance
        - Liability Insurance
        """)

        st.markdown("#### 3. Key Insurance Principles")
        st.markdown("""
        Important principles in insurance include:
        - Utmost Good Faith
        - Insurable Interest
        - Indemnity
        - Subrogation
        - Contribution
        """)

        # Single checkbox for section completion
        st.markdown("---")
        is_section_completed = st.session_state.section_completion_status.get(current_section, False)
        checked_section = st.checkbox(
            f"Mark {current_section} section as complete",
            value=is_section_completed,
            key=f"checkbox_{current_section}_section"
        )
        if checked_section != is_section_completed:
            st.session_state.section_completion_status[current_section] = checked_section
            st.experimental_rerun()

    elif current_section == "Quizzes":
        st.markdown("### 📝 Quizzes")
        render_quiz_section()

        # Single checkbox for section completion
        st.markdown("---")
        is_section_completed = st.session_state.section_completion_status.get(current_section, False)
        checked_section = st.checkbox(
            f"Mark {current_section} section as complete",
            value=is_section_completed,
            key=f"checkbox_{current_section}_section"
        )
        if checked_section != is_section_completed:
            st.session_state.section_completion_status[current_section] = checked_section
            st.experimental_rerun()

    elif current_section == "Resources":
        st.markdown("### 📚 Additional Resources")

        st.markdown("""
        Here are some valuable resources to help you learn more about insurance:

        #### Official Insurance Organizations
        - [Insurance Information Institute](https://www.iii.org/) - Comprehensive information about insurance products and industry trends
        - [National Association of Insurance Commissioners](https://www.naic.org/) - Regulatory information and consumer resources
        - [Insurance Regulatory and Development Authority of India](https://www.irdai.gov.in/) - Indian insurance regulatory body

        #### Learning Resources
        - [Insurance Basics Guide](https://www.iii.org/article/insurance-101) - A comprehensive guide to understanding insurance
        - [Insurance Glossary](https://www.iii.org/glossary) - Common insurance terms and definitions
        - [Insurance Calculators](https://www.iii.org/calculators) - Tools to help you understand insurance needs
        """)

        # Single checkbox for section completion
        st.markdown("---")
        is_section_completed = st.session_state.section_completion_status.get(current_section, False)
        checked_section = st.checkbox(
            f"Mark {current_section} section as complete",
            value=is_section_completed,
            key=f"checkbox_{current_section}_section"
        )
        if checked_section != is_section_completed:
            st.session_state.section_completion_status[current_section] = checked_section
            st.experimental_rerun()

def show_module_details():
    """Display the detailed view of the selected module"""
    st.markdown("""
        <div style='margin-bottom: 2rem;'>
            <h1 style='display: flex; align-items: center; gap: 0.5rem;'>
                🤖 AI Learning Coach
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # Module Selection
    st.markdown("### 📖 Learn")
    st.markdown("#### Learning Module:")
    st.markdown("🔴 Insurance Module")

    # Module Progress
    st.markdown("#### Module Progress")
    insurance_sections = list(load_insurance_module_data().keys())
    render_module_section_progress_bar(insurance_sections)

    # Module Content
    st.markdown("### Module 1")
    
    # Sections
    st.markdown("#### Sections")
    
    # Readings Section
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown("🔴")
    with col2:
        st.markdown("Readings")
    
    # Quizzes Section
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown("⚪")
    with col2:
        st.markdown("Quizzes")

def main():
    """Insurance Module Page"""
    # Initialize session state for the module
    if 'item_completion_status' not in st.session_state:
        st.session_state.item_completion_status = {}
    if 'section_completion_status' not in st.session_state:
        st.session_state.section_completion_status = {}
    if 'quiz_state_module1' not in st.session_state:
        st.session_state.quiz_state_module1 = {
            'submitted': False,
            'answers': {}
        }

    # Show the insurance module content
    show_insurance_module()

if __name__ == "__main__":
    main() 