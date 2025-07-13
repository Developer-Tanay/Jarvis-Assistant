from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifire,
    QueryModifire,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.Model import firstLayerDMM
from Backend.RealtimeSearchEngine import realtimeSearchEngine
from Backend.Automation import translateAndExecute
from Backend.SpeechToText import speechRecognition
from Backend.Chatbot import chatBot
from Backend.TextToSpeech import textToSpeech
from Backend.ReminderTimer import initialize_storage
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
username = env_vars.get("USERNAME")
Assistantname = env_vars.get("ASSISTANT_NAME")
DefaultMessage = f"""{username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {username}. I am doing well. How may i help you?"""

Functions = [
    "open",
    "close",
    "play",
    "system",
    "content",
    "google search",
    "youtube search",
    "reminder",
    "remind me",
    "set timer",
    "timer for",
    "list reminders",
    "list timers",
    "cancel reminder",
    "cancel timer",
    "generate image",
]


def ShowDefaultChatIfNoChats():
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
        if len(file.read()) < 5:
            with open(
                TempDirectoryPath("Database.data"), "w", encoding="utf-8"
            ) as file:
                file.write("")
            with open(
                TempDirectoryPath("Responses.data"), "w", encoding="utf-8"
            ) as file:
                file.write(DefaultMessage)


def ReadChatLogJson():
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
        chatlog_data = json.load(file)
        return chatlog_data


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", username + ":")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + ":")
    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifire(formatted_chatlog))


def ShowChatsOnGUI():
    File = open(TempDirectoryPath("Database.data"), "r", encoding="utf-8")
    Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split("\n")
        result = "\n".join(lines)
        File.close()
        File = open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8")
        File.write(result)
        File.close()


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

    # Initialize reminder and timer system
    try:
        from Backend.ReminderTimer import initialize_storage

        initialize_storage()
    except Exception as e:
        print(f"Error initializing reminder system: {e}")


InitialExecution()


def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = speechRecognition()
    ShowTextToScreen(f" {username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = firstLayerDMM(Query)

    print("")
    print(f"Decision {Decision}")
    print("")
    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    Mearged_query = "".join(
        [
            "".join(i.split()[1:])
            for i in Decision
            if i.startswith("general") or i.startswith("realtime")
        ]
    )

    # Check for image generation requests
    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                # Use translateAndExecute for ALL automation tasks
                from Backend.Automation import translateAndExecute
                import asyncio

                async def get_automation_result():
                    results = []
                    async for result in translateAndExecute(list(Decision)):
                        if result and isinstance(result, str):
                            results.append(result)
                    return results

                # Get the result from automation
                results = run(get_automation_result())

                # Check if it's a command that returns a response (like reminders/timers)
                if any(
                    queries.startswith(response_func)
                    for response_func in [
                        "reminder",
                        "remind me",
                        "set timer",
                        "timer for",
                        "list reminders",
                        "list timers",
                    ]
                ):
                    # These commands return text responses
                    if results:
                        for result in results:
                            ShowTextToScreen(f" {Assistantname} : {result}")
                            SetAssistantStatus("Answering...")
                            textToSpeech(result)
                else:
                    # System commands (mute, unmute, etc.) don't return text but still need confirmation
                    ShowTextToScreen(f" {Assistantname} : Command executed!")
                    SetAssistantStatus("Answering...")
                    textToSpeech("Done!")

                TaskExecution = True
                break

    # Handle image generation requests
    if ImageExecution and not TaskExecution:
        SetAssistantStatus("Generating Image...")
        ShowTextToScreen(f" {Assistantname} : Creating your image...")

        # Write image generation request to file
        os.makedirs("Frontend/Files", exist_ok=True)
        with open(r"Frontend\Files\ImageGeneratoion.data", "w") as file:
            file.write(f" {ImageGenerationQuery}, True")

        try:
            # Start image generation subprocess
            subprocess.Popen(
                ["python", r"Backend\ImageGeneration.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
            )
            ShowTextToScreen(
                f" {Assistantname} : Image generation started! Please wait..."
            )
            SetAssistantStatus("Answering...")
            textToSpeech(
                "I'm generating your image! It will open automatically when ready."
            )
            TaskExecution = True
        except Exception as e:
            error_msg = f"Error starting image generation: {e}"
            print(error_msg)
            ShowTextToScreen(f" {Assistantname} : {error_msg}")
            textToSpeech("Sorry, there was an error generating the image.")
            TaskExecution = True

    # Handle realtime search queries
    if G and R and not TaskExecution:
        SetAssistantStatus("Searching...")
        Answer = realtimeSearchEngine(QueryModifire(Mearged_query))
        ShowTextToScreen(f" {Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        textToSpeech(Answer)
        TaskExecution = True
    elif not TaskExecution:
        # Handle general chat queries
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                Answer = chatBot(QueryModifire(QueryFinal))
                ShowTextToScreen(f" {Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                textToSpeech(Answer)
                TaskExecution = True
                break
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = realtimeSearchEngine(QueryModifire(QueryFinal))
                ShowTextToScreen(f" {Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                textToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = chatBot(QueryModifire(QueryFinal))
                ShowTextToScreen(f" {Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                textToSpeech(Answer)
                SetAssistantStatus("Answering...")
                os._exit(1)


def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")


def SecondThread():

    GraphicalUserInterface()


if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
