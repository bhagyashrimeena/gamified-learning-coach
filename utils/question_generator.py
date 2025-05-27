def generate_questions(topic: str):
    """Simulates dynamic question generation based on topic."""
    questions = []
    
    if topic == "Insurance Fundamentals":
        questions = [
            {
                "question": "What is the primary purpose of insurance?",
                "options": ["Wealth creation", "Risk transfer", "Entertainment", "Tax evasion"],
                "answer": "Risk transfer",
                "explanation": "Insurance primarily serves as a risk transfer mechanism, allowing individuals to protect themselves against potential financial losses."
            },
            {
                "question": "Which principle requires both the insurer and insured to disclose all relevant information?",
                "options": ["Insurable Interest", "Indemnity", "Utmost Good Faith", "Subrogation"],
                "answer": "Utmost Good Faith",
                "explanation": "The principle of utmost good faith requires both parties to be completely honest and transparent."
            },
            {
                "question": "What is 'Insurable Interest'?",
                "options": [
                    "The amount of premium paid",
                    "The legal right to insure something",
                    "The profit made by the insurer",
                    "The age of the insured"
                ],
                "answer": "The legal right to insure something",
                "explanation": "Insurable interest means you would suffer a financial loss if the insured event occurs."
            },
            {
                "question": "The principle of Indemnity aims to:",
                "options": [
                    "Pay more than the actual loss",
                    "Restore the insured to their financial position before the loss",
                    "Punish the insurer",
                    "Create wealth for the insured"
                ],
                "answer": "Restore the insured to their financial position before the loss",
                "explanation": "Indemnity ensures the insured is compensated for their loss, but not profited from it."
            }
        ]
    # Add more topics and questions here as needed, based on your knowledge base structure
    
    return questions 