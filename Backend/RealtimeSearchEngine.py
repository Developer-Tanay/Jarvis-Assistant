# Backend\RealtimeSearchEngine.py

from googlesearch import search
from json import dump, load
from groq import Groq
import datetime
from dotenv import dotenv_values

cnv_vars = dotenv_values(".env")

userName = cnv_vars.get("USERNAME", "User")
assistantName = cnv_vars.get("ASSISTANT_NAME", "Assistant")
groqAPIKey = cnv_vars.get("GROQ_API_KEY")

client = Groq(api_key=groqAPIKey)

system = f"""Hello, I am {userName}, You are a very accurate and advanced AI chatbot named {assistantName} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""


# try to load the chat Log from json file
try:
    with open(r"Data\ChatLog.json", "r") as file:
        messages = load(file)
except:
    with open(r"Data\ChatLog.json", "w") as file:
        dump([], file)

# function to perform Google search and format the results
def googleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    answer += "[end]"
    return answer

# function to clean up the answer by removing emtpty lines and unnecessary spaces
def answerModifier(answer):
    lines = answer.split("\n")
    nonEmptyLines = [line for line in lines if line.strip()]
    modifiedAnswer = "\n".join(nonEmptyLines)
    return modifiedAnswer

# predefined chatbot conversation system message and initial user message
systemChatBot = [
    {"role": "system", "content": system},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello! How can I help you?"}
]

# function to get reaqltime info like the current date and time in a specific format
def information():
    data = ""
    currentDateTime = datetime.datetime.now()
    day = currentDateTime.strftime("%A")
    month = currentDateTime.strftime("%B")
    year = currentDateTime.year
    hour = currentDateTime.strftime("%I")
    minute = currentDateTime.strftime("%M")
    second = currentDateTime.strftime("%S")
    # am_pm = currentDateTime.strftime("%p")
    data += f"Use this Real-time information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minute,  {second} second\n"
    return data

# function to handle realtime search and response generation
def realtimeSearchEngine(prompt):
    global systemChatBot, messages

    # load the chat log from json file
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": f"{prompt}"})

    # add the Google search results to the system chatbot messages
    systemChatBot.append({"role": "system", "content":googleSearch(prompt)})

    # generate the response using Groq client
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=systemChatBot + [{"role": "system", "content": information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    answer = ""

    # concatenate the response chunks from the streaming output
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    # clean up the response
    answer = answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": answer})

    # save the updated chat log to json file
    with open(r"Data\ChatLog.json", "w") as file:
        dump(messages, file, indent=4)

    # remoove the most recent system message from the chat log
    systemChatBot.pop()
    return answerModifier(answer=answer)

# main entry point for testing the realtime search engine
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(realtimeSearchEngine(prompt))
