# J.A.R.V.I.S Voice Assistant

A Python-based voice assistant inspired by Tony Stark's J.A.R.V.I.S. Speaks and listens in real-time using OpenAI, ElevenLabs, and speech recognition.

---

## Features

- Wake-word detection (`"Jarvis"`) to start interactions.
- Continuous conversation mode with natural voice responses.
- Text-to-speech via ElevenLabs API.
- AI responses powered by OpenRouter and Google Gemini Flash.
- Lightweight conversation history management.

---

## Requirements

- Python 3.9+
- [OpenRouter API Key](https://openrouter.ai)
- [ElevenLabs API Key](https://beta.elevenlabs.io/)
- pip packages: install via `requirements.txt`

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/wavesam/jarvis.git
cd jarvis
Create a virtual environment and activate it:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate      # macOS/Linux
# OR venv\Scripts\activate    # Windows
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Set up environment variables:

bash
Copy
Edit
cp .env.example .env
# Edit .env with your API keys
Usage
Run the assistant:

bash
Copy
Edit
python main.py
Say "Jarvis" to wake the assistant.

Speak naturally to interact.

Say "thank you" to exit conversation mode.

Notes
Do not commit your .env file or virtual environment (venv/) to GitHub.

Only English is supported in AI responses.

Designed for macOS/Linux; minor tweaks may be needed for Windows.

License
MIT License

yaml
Copy
Edit

---

If you want, I can also create a **`.env.example`** and **`requirements.txt`** that match this README, so your repo is fully ready to go. Do you want me to do that?
