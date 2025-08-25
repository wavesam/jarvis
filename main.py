import os
from dotenv import load_dotenv 
load_dotenv()

from openai import OpenAI
import speech_recognition as sr
import requests
import pygame
import io
import time
import threading
from queue import Queue
from collections import deque

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
recognizer = sr.Recognizer()
pygame.mixer.init()

conversation_history = deque(maxlen=6)
audio_queue = Queue()
conversation_mode = False

ENERGY_THRESHOLD = 300  # Optimized constant value
PAUSE_THRESHOLD = 0.5
DYNAMIC_ENERGY = False  # Disable for faster response

def adjust_microphone_sensitivity(source):
    try:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        recognizer.energy_threshold = ENERGY_THRESHOLD
        recognizer.pause_threshold = PAUSE_THRESHOLD
        recognizer.dynamic_energy_threshold = DYNAMIC_ENERGY
    except Exception:
        recognizer.energy_threshold = ENERGY_THRESHOLD
        recognizer.pause_threshold = PAUSE_THRESHOLD
        recognizer.dynamic_energy_threshold = DYNAMIC_ENERGY

def listen_continuous(wake_word="jarvis"):
    global conversation_mode
    with sr.Microphone() as source:
        adjust_microphone_sensitivity(source)
        
        while True:
            try:
                audio = recognizer.listen(source, timeout=0.6, phrase_time_limit=2)
                text = recognizer.recognize_google(audio).lower()
                
                if text.startswith(wake_word) or wake_word in text:
                    print(f"You: {text}")
                    if text.startswith(wake_word):
                        command = text[len(wake_word):].strip() or "greeting"
                    else:
                        command = text.split(wake_word, 1)[1].strip() or "greeting"
                    conversation_mode = True
                    return command
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception:
                time.sleep(0.2)

def listen_in_conversation_mode():
    global conversation_mode
    
    with sr.Microphone() as source:
        adjust_microphone_sensitivity(source)
        recognizer.pause_threshold = 0.6
        
        while conversation_mode:
            try:
                audio = recognizer.listen(source, timeout=0.8, phrase_time_limit=8)
                text = recognizer.recognize_google(audio).lower()
                
                if text:
                    print(f"You: {text}")
                    if "thank you" in text:
                        conversation_mode = False
                        return "exit_conversation"
                    
                    return text
                    
            except sr.UnknownValueError:
                continue
            except sr.WaitTimeoutError:
                continue
            except Exception:
                continue
    
    return ""

def audio_worker():
    while True:
        text = audio_queue.get()
        if text is None:
            break
        speak(text)
        audio_queue.task_done()

def speak(text):
    print(f"AI: {text}")
    
    try:
        ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
        VOICE_ID = "pNInz6obpgDQGcFmaJgB"
        
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
            }
        )
        
        if response.status_code == 200:
            audio_buffer = io.BytesIO(response.content)
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
    except Exception:
        pass

def chat_with_ai(prompt):
    system_message = "You are J.A.R.V.I.S., Tony Stark's AI. Speak calmly, politely, and intelligently. Call me Samuel, address user as 'Sir' when needed. Be precise, witty, under thirty words, and only use english words with never any special symbols. Add some light banter since you are JARVIS. For any math equations, write it out in word form (such as one over x instead of 1/x)."
    
    messages = [{"role": "system", "content": system_message}]
    
    for entry in conversation_history:
        messages.append(entry)
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model="google/gemini-flash-1.5",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
            extra_headers={"HTTP-Referer": "http://localhost:3000"}
        )
        
        ai_response = response.choices[0].message.content
        
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response
    except Exception:
        return "I'm having trouble connecting right now. Please try again."

if __name__ == "__main__":
    audio_thread = threading.Thread(target=audio_worker, daemon=True)
    audio_thread.start()
    
    try:
        while True:
            if not conversation_mode:
                command = listen_continuous("jarvis")
                response = chat_with_ai(command or "greeting")
                audio_queue.put(response)
            else:
                command = listen_in_conversation_mode()
                
                if command == "exit_conversation":
                    audio_queue.put("You're welcome Samuel. I'll be waiting for your call.")
                elif command:
                    response = chat_with_ai(command)
                    audio_queue.put(response)
                    
    except KeyboardInterrupt:
        audio_queue.put(None)
        audio_thread.join()