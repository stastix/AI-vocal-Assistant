from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha

# Speech engine initialization
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0=male, 1=female
activationWord = "Computer"

# 1st Method
def speak(text, rate=120):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def parseCommand():
    listener = sr.Recognizer()
    print("Listening to your commands")

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)

    try:
        print('Recognizing speech ...')
        query = listener.recognize_google(input_speech, language='en_gb')
        print(f"The input speech was: {query}")
    except Exception as exception:
        print("I did not quite catch that")
        speak("Sorry, couldn't hear that.")
        print(exception)
        return "None"
    
    
    return query

# Main loop
if __name__ == '__main__':
    speak('All systems nominal.')
    
    
    while True:
        # Parse
        query = parseCommand().lower().split()  # Corrected the function call and added missing parentheses
        if query[0] == activationWord:
            query.pop(0)
            if query[0] == 'say':
                if 'hello' in query:
                    speak("Greeting, all.")
            
                else: 
                    query.pop(0) 
                    speech=' '.join(query)
                    speak(speech)
