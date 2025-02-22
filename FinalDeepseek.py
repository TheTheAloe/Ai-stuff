import requests
import json
import pyttsx3
import speech_recognition as sr
import sys  # Import sys for exiting the program
import time  # Import time for sleep functionality

# Set up the base URL for the local Ollama API
url = "http://localhost:11434/api/chat"

# Initialize the pyttsx3 engine for speech output
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Set voice (0 for male, 1 for female)

# Store previous conversation context
conversation_history = []

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
def listen_for_wakeword(wakeword="hey ai"):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Listening for wakeword...")
        recognizer.adjust_for_ambient_noise(source)  # Adjusts for ambient noise
        while True:
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio).lower()  # Use Google's speech recognition
                print(f"Heard: {text}")
                if wakeword in text:  # If the wakeword is detected
                    print(f"Wakeword '{wakeword}' detected. Let's chat!")
                    return True
            except sr.UnknownValueError:
                pass  # Ignore unrecognized audio
            except sr.RequestError:
                print("Sorry, I'm having trouble connecting to the service. Please check your internet connection.")
                return False

# Function to capture user input and interact with the AI
def listen_and_respond():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Listening for user input...")
        recognizer.adjust_for_ambient_noise(source)  # Adjusts for ambient noise
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)  # Use Google's speech recognition
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Could you please repeat?")
        engine.say("Sorry, I didn't catch that. Could you please repeat?")
        engine.runAndWait()
        return None
    except sr.RequestError:
        print("Sorry, I'm having trouble connecting to the service. Please check your internet connection.")
        return None

# Main loop to have a conversation after detecting wakeword
def main():
    while True:
        # Continuously listen for the wakeword
        if listen_for_wakeword():  # Detect the wakeword
            # Speak the reminder once after detecting the wakeword
            engine.say("The wakeword Hey Ai has woke me up! To end this chat say End Chat. To terminate the script say Kill.")
            engine.runAndWait()

            is_in_conversation = True  # Set the flag to indicate we're in a conversation
            while is_in_conversation:  # Start the conversation after wakeword is detected
                user_input = listen_and_respond()  # Capture input from the microphone
                if user_input:
                    # Check for "end chat" command to stop the conversation
                    if "end chat" in user_input.lower():
                        print("Ending chat... Returning to wakeword listening.")
                        engine.say("Goodbye! I'll be listening for the wakeword again.")
                        engine.runAndWait()
                        is_in_conversation = False  # End conversation and go back to listening for the wakeword

                    # Check for "kill" command to terminate the script
                    if "kill" in user_input.lower():
                        print("Terminating the script...")
                        engine.say("Terminating the script. Goodbye!")
                        engine.runAndWait()
                        sys.exit()  # Exit the script completely
                    
                    # Add the user input to conversation history
                    conversation_history.append({"role": "user", "content": user_input})
                    
                    # Get AI's response
                    generated_text = generate_text(user_input)  # Get AI's response
                    print(f"AI says: {generated_text}")  # Print AI's response
                    
                    # Add AI's response to conversation history
                    conversation_history.append({"role": "assistant", "content": generated_text})
                    
                    engine.say(generated_text)  # Use pyttsx3 to speak the response
                    engine.runAndWait()  # Wait for speech to finish

if __name__ == "__main__":
    main()
