import requests
import json
import pyttsx3

# Set up the base URL for the local Ollama API
url = "http://localhost:11434/api/chat"

# Example prompt for the AI to generate text
prompt = "hi."

# Define the payload (your input prompt)
payload = {
    "model": "deepseek-r1:32b",  # Replace with the model name you're using
    "messages": [{"role": "user", "content": prompt}]
}

# Function to generate text by making a request to the API
def generate_text(prompt):
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

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Set properties for the speech engine
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

# Get AI-generated text using the generate_text function
generated_text = generate_text(prompt)

# Output the generated text
print(f"AI says: {generated_text}")

# Use pyttsx3 to speak the generated text
engine.say(generated_text)

# Wait for speech to finish
engine.runAndWait()
