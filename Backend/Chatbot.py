# Backend/Chatbot.py

from groq import Groq
from json import dump, load
import datetime
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

userName = env_vars.get("USERNAME")
assistantName = env_vars.get("ASSISTANT_NAME")
groqAPIKey = env_vars.get("GROQ_API_KEY")  # Fixed typo: was "grokAPIKey"

# Validate required environment variables
if not groqAPIKey:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")

if not userName:
    userName = "User"  # Default fallback

if not assistantName:
    assistantName = "Assistant"  # Default fallback

# Initialize Groq client
try:
    client = Groq(api_key=groqAPIKey)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    exit(1)

# System message
system = f"""Hello, I am {userName}, You are a very accurate and advanced AI chatbot named {assistantName} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

def ensure_data_directory():
    """Ensure the Data directory exists."""
    if not os.path.exists("Data"):
        os.makedirs("Data")

def load_chat_history():
    """Load chat history from JSON file."""
    ensure_data_directory()
    chat_log_path = os.path.join("Data", "ChatLog.json")
    
    try:
        with open(chat_log_path, "r", encoding="utf-8") as f:
            return load(f)
    except FileNotFoundError:
        # Create empty chat log if file doesn't exist
        with open(chat_log_path, "w", encoding="utf-8") as f:
            dump([], f)
        return []
    except Exception as e:
        print(f"Error loading chat history: {e}")
        return []

def save_chat_history(messages):
    """Save chat history to JSON file."""
    ensure_data_directory()
    chat_log_path = os.path.join("Data", "ChatLog.json")
    
    try:
        with open(chat_log_path, "w", encoding="utf-8") as f:
            dump(messages, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving chat history: {e}")

def realTimeInformation():
    """Get current date and time information."""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d %B %Y")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    time = current_date_time.strftime("%H:%M:%S")  # Combined time format
    
    data = f"Please use this real-time information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\nTime: {time}\n"
    return data

def answerModifier(answer):
    """Remove empty lines from the answer."""
    if not answer:
        return ""
    
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer.strip()

def chatBot(query, max_retries=3):
    """Send user query to the chatbot and return the AI's response."""
    
    if not query or not query.strip():
        return "Please provide a valid query."
    
    for attempt in range(max_retries):
        try:
            # Load current chat history
            messages = load_chat_history()
            
            # Add user message
            messages.append({"role": "user", "content": query.strip()})
            
            # Prepare system messages
            system_messages = [
                {"role": "system", "content": system},
                {"role": "system", "content": realTimeInformation()}
            ]
            
            # Create completion
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=system_messages + messages,
                max_tokens=1024,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )
            
            # Collect response
            answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content
            
            # Clean up the answer
            answer = answer.replace("</s>", "").strip()
            
            if not answer:
                return "I apologize, but I couldn't generate a response. Please try again."
            
            # Add assistant response to messages
            messages.append({"role": "assistant", "content": answer})
            
            # Save updated chat history
            save_chat_history(messages)
            
            return answerModifier(answer)
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt == max_retries - 1:
                # Last attempt failed, reset chat log and return error
                print("All attempts failed. Resetting chat history.")
                save_chat_history([])
                return f"I'm sorry, I encountered an error: {str(e)}. Please try again."
            
            # Wait a bit before retrying
            import time
            time.sleep(1)
    
    return "I'm sorry, I couldn't process your request. Please try again."

def main():
    """Main function to run the chatbot."""
    print(f"Welcome! I'm {assistantName}, your AI assistant.")
    print("Type 'exit', 'quit', or 'bye' to end the conversation.")
    print("-" * 50)
    
    try:
        while True:
            user_input = input("\nEnter your question: ").strip()
            
            # Handle exit conditions
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print(f"Goodbye! Have a great day!")
                break
            
            if not user_input:
                print("Please enter a question.")
                continue
            
            # Get and display response
            response = chatBot(user_input)
            print(f"\n{assistantName}: {response}")
            
    except KeyboardInterrupt:
        print(f"\n\nGoodbye! Have a great day!")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()