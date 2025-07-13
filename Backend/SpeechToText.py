# Backend/SpeechToText.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

env_vars = dotenv_values(".env")
# Get the input language setting from the environment variables
inputLanguage = env_vars.get("INPUT_LANGUAGE")

# Define the html code for a speech recognition interface
htmlCode = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>"""

# Replace the language settings In the html code with input language from the environment variables
htmlCode = str(htmlCode).replace(
    "recognition.lang = '';", f"recognition.lang = '{inputLanguage}';"
)

# Write the modified html code to a file
with open(r"Data\Voice.html", "w") as f:
    f.write(htmlCode)

# get The current working directory
currentDirectory = os.getcwd()
# Generate the file path for html file
link = f"{currentDirectory}/Data/Voice.html"

# set Chrome options for the web drivers
chromeOptions = Options()
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
chromeOptions.add_argument(f"user-agent={userAgent}")
chromeOptions.add_argument("--use-fake-ui-for-media-stream")
chromeOptions.add_argument("--use-fake-device-for-media-stream")
chromeOptions.add_argument("--headless-new")

# Global variable to hold the driver
driver = None


# Function to initialize the Chrome WebDriver only when needed
def initialize_driver():
    global driver
    if driver is None:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chromeOptions)
    return driver


# Define the path for temporary files
temDirPath = rf"{currentDirectory}/Frontend/Files"


# Function to set the assistant's status writing it to a file
def setAssistantStatus(status):
    with open(rf"{temDirPath}/Status.data", "w", encoding="utf-8") as f:
        f.write(status)


# Function to modify a query To ensure proper punctuation and formatting
def queryModifier(query):
    newQuery = query.strip().capitalize()
    queryWords = newQuery.split()
    questionWords = [
        "what",
        "who",
        "where",
        "when",
        "why",
        "how",
        "which",
        "whose",
        "whom",
        "is",
        "are",
        "do",
        "does",
        "did",
        "can you",
        "can",
        "could",
        "will",
        "would",
        "should",
        "what's",
        "who's",
        "where's",
        "when's",
        "why's",
        "how's",
        "which's",
        "whose's",
        "whom's",
    ]

    # Check if the query is a question and add a question mark if it is
    if any(word + " " in newQuery for word in questionWords):
        if queryWords[-1][-1] in [".", "!", "?"]:
            newQuery = newQuery[:-1] + "?"
        else:
            newQuery += "?"
    else:
        # add a period if query is not a question
        if queryWords[-1][-1] in [".", "!", "?"]:
            newQuery = newQuery[:-1] + "."
        else:
            newQuery += "."

    return newQuery.capitalize()


# Function to translate text into english Using the mttranslate library
def universalTranslator(text):
    englishTranslation = mt.translate(text, "en", "auto")
    return englishTranslation.capitalize()


# Function to perform speech recognition using the Chrome WebDriver
def speechRecognition():
    # Initialize the driver if not already done
    current_driver = initialize_driver()

    # Open the HTML file in the Chrome WebDriver
    current_driver.get("file:///" + link)
    # start the speech recognition process By clicking the start button
    current_driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            # Get the recognised text from the HTML output element
            text = current_driver.find_element(by=By.ID, value="output").text

            if text:
                # Stop recognising by clicking the stop button
                current_driver.find_element(by=By.ID, value="end").click()

                # If the input language is English, return the modified query
                if inputLanguage.lower() == "en" or "en" in inputLanguage.lower():
                    return queryModifier(text)
                else:
                    # If the input language is not English, translate the text to English and return the modified query
                    setAssistantStatus("Translating...")
                    translatedText = universalTranslator(text)
                    return queryModifier(translatedText)
        except Exception as e:
            pass


# main execution block
if __name__ == "__main__":
    while True:
        text = speechRecognition()
        print(text)
