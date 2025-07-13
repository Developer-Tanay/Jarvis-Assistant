from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import requests
import threading
from datetime import datetime, timedelta
import time
import re
import subprocess
import keyboard
import os
import asyncio
from .ReminderTimer import (
    set_reminder,
    set_timer,
    list_reminders,
    list_timers,
    cancel_reminder,
    cancel_timer,
)


env_vars = dotenv_values(".env")
grokAPIKey = env_vars.get("GROQ_API_KEY")


# define CSS classes for parsing specific elements in HTML content
classes = [
    "zCubwf",
    "hgKElc",
    "LTKOO sY7ric",
    "ZOLcW",
    "gsrt vk_bk FzvWSb YwPhnf",
    "pclqee",
    "tw-Data-text tw-text-small tw-ta",
    "IZ6rdc",
    "05uR6d LTKOO",
    "vlzY6d",
    "webanswers-webanswers_table_webanswers-table",
    "dDoNo ikb4Bb gsrt",
    "sXLa0e",
    "LWkfKe",
    "VQF4g",
    "qv3Wpe",
    "kno-rdesc",
    "SPZz6b",
]


# Define a user agent for making web requests
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Brave"


# initialize the groq client with api key
client = Groq(api_key=grokAPIKey)


# predefined professional responses for user interactions
professional_responses = {
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
}

# list to store chatbot messages
messages = []

# Global storage for active reminders and timers
active_reminders = []
active_timers = []


# Function to speak reminder/timer notifications
def speak_notification(message):
    try:
        import sys

        sys.path.append(os.path.join(os.getcwd(), "Backend"))
        from TextToSpeech import TextToSpeech

        TextToSpeech(message)
    except ImportError:
        try:
            with open(
                rf"{os.getcwd()}\Frontend\Files\Responses.data", "w", encoding="utf-8"
            ) as file:
                file.write(message)
        except:
            print(f"Notification: {message}")


# system message to provide context to the chat bot
systemChatBot = [
    {
        "role": "system",
        "content": f"Hello, I am {os.environ['USERNAME']}, You're a content writer. You have to write content like letters, emails, applications, codes, essays, notes, poems, songs  and other professional content. You are a professional content writer. You are very professional and you always write in a professional way by following the standard approach.",
    }
]


def googleSearch(topic):
    search(topic)
    return True


# function to generate content using AI and save it to a file
def content(topic):

    # nested function to open a file in Notepad
    def openNotepad(file):
        defaultTextEditor = "notepad.exe"
        subprocess.Popen([defaultTextEditor, file])

    # nested function to generate content using the AI chat bot
    def contentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model="mistral-saba-24b",
            messages=systemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
        )

        answer = ""  # Initialize an empty string for answer

        # process streamed response chunk
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")  # remove unwanted tokens from the response
        messages.append({"role": "assistant", "content": f"{answer}"})
        return answer

    topic: str = topic.replace("content ", "")
    contentByAI = contentWriterAI(topic)

    # Save the generated content into a text file
    with open(f"{topic}.txt", "w", encoding="utf-8") as file:
        file.write(contentByAI)

    # Open the generated content in Notepad
    openNotepad(f"{topic}.txt")
    return True


# Function to search for a topic on Youtube
def youtubeSearch(topic):
    url4Search = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url4Search)
    return True


# Function to play a video on Youtube
def youtubePlay(query):
    playonyt(query)
    return True


# # function to open an application or a relevant web page
# This is comment out because it has some errors so we have created Another function below with better accuracy
# def openApp(app, sess=requests.session()):

#     try:
#         appopen(app, match_closest=True, output=True, throw_error=True)
#         return True
#     except:
#         # Nested function to extract links from HTML content
#         def extractLinks(html):
#             if html is None:
#                 return []
#             soup = BeautifulSoup(html, "html.parser")
#             links = soup.find_all("a", {'jsname': "UWckNb"})
#             return [link.get("href") for link in links]

#         # function to perform a google search and retrieve HTML
#         def searchGoogle(query):
#             headers = {"User-Agent": useragent}
#             url = f"https://www.google.com/search?q={query}"
#             response = sess.get(url, headers=headers)

#             if response.status_code == 200:
#                 return response.text
#             else:
#                 print(f"Error: Unable to fetch search results for {query}")
#                 return None

#         try:
#             html = searchGoogle(app) # Perform a Google search for the app

#             if html:
#                 links = extractLinks(html)
#                 if links and len(links) > 0:  # Check if links were found
#                     webopen(links[0]) # open the first link in a web browser
#                     return True
#                 else:
#                     print(f"No direct links found for {app}, trying general search")

#             # Fallback to direct Google search
#             search_url = f"https://www.google.com/search?q={app}"
#             webopen(search_url)
#             return True

#         except Exception as e:
#             print(f"Error opening web resource for {app}: {str(e)}")
#             return False


# function to open an application or a relevant web page
def openApp(app):
    try:
        # Try local application first
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        # Fast fallback - instant URL opening for known services
        print(f"Local app '{app}' not found. Using fast URL detection...")

        # Special cases for popular services (instant opening - no network delay)
        special_urls = {
            "chat gpt": "https://chat.openai.com",
            "openai": "https://chat.openai.com",
            "claude": "https://claude.ai",
            "bard": "https://bard.google.com",
            "gemini": "https://gemini.google.com",
            "perplexity": "https://perplexity.ai",
            "github": "https://github.com",
            "stackoverflow": "https://stackoverflow.com",
            "reddit": "https://reddit.com",
            "discord": "https://discord.com",
            "slack": "https://slack.com",
            "notion": "https://notion.so",
            "figma": "https://figma.com",
            "canva": "https://canva.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "twitter": "https://www.twitter.com",
            "youtube": "https://www.youtube.com",
            "gmail": "https://www.gmail.com",
            "drive": "https://drive.google.com",
            "docs": "https://docs.google.com",
            "sheets": "https://sheets.google.com",
            "slides": "https://slides.google.com",
            "whatsapp": "https://web.whatsapp.com",
            "telegram": "https://web.telegram.org",
            "zoom": "https://zoom.us",
            "teams": "https://teams.microsoft.com",
            "spotify": "https://open.spotify.com",
            "netflix": "https://netflix.com",
        }

        app_lower = app.lower()
        if app_lower in special_urls:
            webopen(special_urls[app_lower])
            print(f"✅ Opened {special_urls[app_lower]}")
            return True

        # For unknown apps, try common URL pattern (www.{app}.com)
        try:
            common_url = f"https://www.{app.lower()}com"
            webopen(common_url)
            print(f"✅ Trying {common_url}")
            return True
        except:
            # Final fallback - Google search
            search_url = f"https://www.google.com/search?q={app}"
            webopen(search_url)
            print(f"🔍 Opened search for '{app}'")
            return True


# Function to close an application
def closeApp(app):

    if "chrome" in app.lower():
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            print(f"Error: Unable to close {app}. It may not be running.")
            return False


# function to execute system level commands
def system(command):
    # Clean up the command by removing punctuation and extra spaces
    command = command.strip().rstrip(".").strip()

    def mute():
        # Use the standard volume mute key
        keyboard.press_and_release("volume_mute")

    def unmute():
        # Use the standard volume mute key (toggles mute/unmute)
        keyboard.press_and_release("volume_mute")

    def volumeUp():
        keyboard.press_and_release("volume up")

    def volumeDown():
        keyboard.press_and_release("volume down")

    def shutdown():
        subprocess.run("shutdown /s /t 1", shell=True)

    # execute appropriate command
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volumeUp()
    elif command == "volume down":
        volumeDown()
    elif command == "shutdown":
        shutdown()
    elif "shutdown" in command:  # Handle variations like "shutdown computer"
        shutdown()
    else:
        print(f"Unknown system command: {command}")
        return False

    return True


# asynchronous function to translate and execute user commands
async def translateAndExecute(command):

    funcs = []  # list to store asynchronous tasks

    for command in command:

        if command.startswith("open "):

            if "open it " in command:
                pass

            if "open file " in command:
                pass

            else:
                fun = asyncio.to_thread(openApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass

        elif command.startswith("realtime "):
            pass

        elif command.startswith("close "):
            fun = asyncio.to_thread(closeApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(youtubePlay, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(
                googleSearch, command.removeprefix("google search ")
            )
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(
                youtubeSearch, command.removeprefix("youtube search ")
            )
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(system, command.removeprefix("system "))
            funcs.append(fun)

        elif command.startswith("reminder "):
            fun = asyncio.to_thread(set_reminder, command)
            funcs.append(fun)

        elif command.startswith("remind me ") or "remind me " in command:
            fun = asyncio.to_thread(set_reminder, command)
            funcs.append(fun)

        elif (
            command.startswith("set timer ")
            or command.startswith("timer for ")
            or "set a timer" in command
        ):
            fun = asyncio.to_thread(set_timer, command)
            funcs.append(fun)

        elif command.startswith("list reminders") or command == "show reminders":
            fun = asyncio.to_thread(list_reminders)
            funcs.append(fun)

        elif command.startswith("list timers") or command == "show timers":
            fun = asyncio.to_thread(list_timers)
            funcs.append(fun)

        elif command.startswith("cancel reminder"):
            fun = asyncio.to_thread(cancel_reminder)
            funcs.append(fun)

        elif command.startswith("cancel timer"):
            fun = asyncio.to_thread(cancel_timer)
            funcs.append(fun)

        else:
            print(f"No command found for {command}")

    results = await asyncio.gather(*funcs)  # gather results from all tasks

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result


# asynchronous function to automate command execution
async def automation(command: list[str]):

    async for result in translateAndExecute(command):
        pass

    return True


# if __name__ == "__main__":
#     asyncio.run(automation(["open telegram", "google search Python programming", "play Python tutorial on YouTube"]))
