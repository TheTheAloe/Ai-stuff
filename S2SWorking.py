import requests
import json
import pyttsx3
import speech_recognition as sr

# Set up the base URL for the local Ollama API
url = "http://localhost:11434/api/chat"

# Initialize the pyttsx3 engine for speech output
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Set voice (0 for male, 1 for female)

# Function to generate text by making a request to the API
def generate_text(prompt):
    payload = {
        "model": "deepseek-r1:32b",  # Replace with the model name you're using
        "messages": [{"role": "user", "content": prompt}]
    }
    # Send the HTTP POST request with streaming enabled
    response = requests.post(url, json=payload, stream=True)
    
    # Check the response status
    if response.status_code == 200:
        print("Streaming response from Ollama:")
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:  # Ignore empty lines
                try:
                    # Parse each line as a JSON object
                    json_data = json.loads(line)
                    # Extract and accumulate the assistant's message content
                    if "message" in json_data and "content" in json_data["message"]:
                        full_response += json_data["message"]["content"]
                except json.JSONDecodeError:
                    print(f"\nFailed to parse line: {line}")
        return full_response
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return "Error generating text."

# Function to capture speech from the microphone and convert to text
def listen():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjusts for ambient noise
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)  # Use Google's speech recognition
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Could you please repeat?")
        return None
    except sr.RequestError:
        print("Sorry, I'm having trouble connecting to the service. Please check your internet connection.")
        return None

# Main loop to have a conversation
def main():
    while True:
        user_input = listen()  # Capture input from the microphone
        if user_input:
            generated_text = generate_text(user_input)  # Get AI's response
            print(f"AI says: {generated_text}")  # Print AI's response
            engine.say(generated_text)  # Use pyttsx3 to speak the response
            engine.runAndWait()  # Wait for speech to finish

if __name__ == "__main__":
    main()
