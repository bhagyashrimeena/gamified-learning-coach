# AI-Personalized Learning Coach 🤖📚

An intelligent learning platform that provides personalized coaching for customer service agents using local AI models.

## 🌟 Features

- Daily microlearning cards with skill-focused lessons
- Interactive roleplay simulations using local LLMs (Ollama)
- Real-time voice analysis and feedback
- Progress tracking and skill analytics
- Gamified learning experience with achievements
- Adaptive learning recommendations

## 🛠️ Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama**
   - Download and install Ollama from [ollama.ai](https://ollama.ai)
   - Pull the Mistral model:
     ```bash
     ollama pull mistral
     ```

3. **Download Vosk Model**
   - Download the Vosk model for speech recognition
   - Place it in the `assets/vosk-model` directory

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
ai-learning-coach/
├── app.py              # Main Streamlit application
├── microlearning.py    # Daily learning cards engine
├── roleplay_chat.py    # Chat-based roleplay system
├── voice_prompt.py     # Voice analysis and feedback
├── dashboard.py        # Progress tracking and analytics
├── achievements.py     # Gamification system
├── assets/            # Static assets and models
│   └── vosk-model/    # Speech recognition model
└── requirements.txt    # Project dependencies
```

## 🎯 Usage

1. Launch the application using `streamlit run app.py`
2. Complete your daily learning card
3. Practice with AI roleplay scenarios
4. Track your progress in the dashboard
5. Earn achievements as you improve

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 