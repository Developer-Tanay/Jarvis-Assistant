# Backend/Model.py

import cohere
from rich import print
from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Retrieve the Cohere API key from environment variables
cohere_api_key = env_vars.get("COHERE_API_KEY")

if not cohere_api_key:
    raise ValueError(
        "COHERE_API_KEY not found in environment variables. Please check your .env file."
    )

# Initialize the Cohere client with the API key
try:
    co = cohere.Client(cohere_api_key)
except Exception as e:
    print(f"Error initializing Cohere client: {e}")
    exit(1)

# Define a list of organized function keywords for task categorization
funcs = [
    "general",
    "realtime",
    "open",
    "exit",
    "close",
    "generate image",
    "system",
    "google search",
    "youtube search",
    "play",
    "reminder",
    "set timer",
    "list reminders",
    "list timers",
    "content",
]

# Define the preamble that guides the AI model on how to categorize queries
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'set timer (duration)' if a query is asking to set a timer like 'set a timer for 5 minutes', 'timer for 30 seconds', 'set timer 1 hour' respond with 'set timer 5 minutes', 'set timer 30 seconds', 'set timer 1 hour' etc.
-> Respond with 'list reminders' if a query is asking to show, list, or get reminders like 'show me my reminders', 'list reminders', 'give me the reminders', 'what are my reminders' etc.
-> Respond with 'list timers' if a query is asking to show, list, or get timers like 'show my timers', 'list timers', 'what timers are running' etc.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Define a chat history with predefined User chatbot interactions for context
chatHistory = [
    {"role": "USER", "message": "how are you?"},
    {"role": "CHATBOT", "message": "general how are you?"},
    {"role": "USER", "message": "what is the weather today?"},
    {"role": "CHATBOT", "message": "realtime what is the weather today?"},
    {"role": "USER", "message": "open facebook and instagram."},
    {"role": "CHATBOT", "message": "open facebook, open instagram."},
    {"role": "USER", "message": "close whatsapp."},
    {"role": "CHATBOT", "message": "close whatsapp."},
    {"role": "USER", "message": "play my favorite song."},
    {"role": "CHATBOT", "message": "play my favorite song."},
    {"role": "USER", "message": "Open chrome and tell me about Elon Musk."},
    {"role": "CHATBOT", "message": "open chrome, realtime tell me about Elon Musk."},
    {
        "role": "USER",
        "message": "What is today's date and by the way remind me to call mom at 5:30pm.",
    },
    {
        "role": "CHATBOT",
        "message": "general what is today's date, reminder 5:30pm call mom.",
    },
    {"role": "USER", "message": "set a timer for 5 minutes."},
    {"role": "CHATBOT", "message": "set timer 5 minutes."},
    {"role": "USER", "message": "give me the reminders."},
    {"role": "CHATBOT", "message": "list reminders."},
    {"role": "USER", "message": "show my timers."},
    {"role": "CHATBOT", "message": "list timers."},
    {"role": "USER", "message": "what are my reminders?"},
    {"role": "CHATBOT", "message": "list reminders."},
    {"role": "USER", "message": "generate an image of a sunset over mountains."},
    {"role": "CHATBOT", "message": "generate image sunset over mountains."},
    {"role": "USER", "message": "create a picture of a cute cat."},
    {"role": "CHATBOT", "message": "generate image cute cat."},
    {"role": "USER", "message": "make an image showing a futuristic city."},
    {"role": "CHATBOT", "message": "generate image futuristic city."},
    {"role": "USER", "message": "chat with me."},
    {"role": "CHATBOT", "message": "general chat with me."},
]


def firstLayerDMM(prompt: str = "test"):
    try:
        # Create a streaming chat session with the Cohere model
        stream = co.chat_stream(
            model="command-r-plus",
            message=prompt,
            temperature=0.1,  # Lower temperature for more consistent responses
            chat_history=chatHistory,
            prompt_truncation="OFF",
            connectors=[],
            preamble=preamble,  # Add the preamble here
        )

        # Initialize an empty string to store the generated response
        response = ""

        # Iterate over the events in the streamed responses from the model
        for event in stream:
            if event.event_type == "text-generation":
                response += event.text

        # Clean and process the response
        response = response.strip().replace("\n", "")

        # Handle empty response
        if not response:
            return [f"general {prompt}"]

        # Split by comma and clean each part
        response_parts = [part.strip() for part in response.split(",")]

        # Filter valid tasks
        valid_tasks = []
        for task in response_parts:
            task_lower = task.lower()
            for func in funcs:
                if task_lower.startswith(func.lower()):
                    valid_tasks.append(task)
                    break

        # If no valid tasks found, default to general
        if not valid_tasks:
            valid_tasks = [f"general {prompt}"]

        return valid_tasks

    except Exception as e:
        print(f"Error in firstLayerDMM: {e}")
        return [f"general {prompt}"]  # Fallback response


# Entry point for the script
if __name__ == "__main__":
    print("Decision Making Model started. Type 'exit' or 'quit' to stop.")

    try:
        while True:
            user_input = input(">>> ").strip()

            # Handle exit conditions
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break

            if not user_input:
                print("Please enter a query.")
                continue

            result = firstLayerDMM(user_input)
            print(result)

    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
