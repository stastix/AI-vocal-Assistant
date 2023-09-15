from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import keyboard 
import math  
import pywhatkit as kit 
import requests 


import openai

# Load credentials
import os
from dotenv import load_dotenv
load_dotenv() 

# Google TTS
import google.cloud.texttospeech as tts
import pygame
import time

# Mute ALSA errors...
from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p) 

#get weather 
def get_weather_data(api_key, city):
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(base_url)
    weather_data = response.json()
    return weather_data


def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    try: 
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        print('')

### PARAMETERS ###
activationWords = ['computer', 'calcutron', 'shodan', 'showdown']
tts_type = 'local' # google or local

# Local speech engine initialisation
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # 0 = male, 1 = female

# Google TTS client
def google_text_to_wav(voice_name: str, text: str):
    language_code = "-".join(voice_name.split("-")[:2])

    # Set the text input to be synthesized
    text_input = tts.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the voice name
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )

    # Select the type of audio file you want returned
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    return response.audio_content

# Configure browser
# Set the path
chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
# Register the browser
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# Wolfram Alpha client
appId = 'E97784-2U55VT546J' 
wolframClient = wolframalpha.Client(appId)

def speak(text, rate = 120): 
    time.sleep(0.3)
    try:      
        if tts_type == 'local': 
            
            engine.setProperty('rate', rate) 
            engine.say(text, 'txt')
            engine.runAndWait()
        if tts_type == 'google':
            speech = google_text_to_wav('en-US-News-K', text)
            pygame.mixer.init(frequency=12000, buffer = 512)
            speech_sound = pygame.mixer.Sound(speech)
            speech_length = int(math.ceil(pygame.mixer.Sound.get_length(speech_sound)))
            speech_sound.play()
            time.sleep(speech_length)
            pygame.mixer.quit()
 
    except KeyboardInterrupt:
        try:
            if tts_type == 'google':
                pygame.mixer.quit()
        except:
            pass
        return 
        
            


def parseCommand():
    with noalsaerr():
        listener = sr.Recognizer()
        print('Listening for a command')

        with sr.Microphone() as source:
            listener.pause_threshold = 2
            input_speech = listener.listen(source)

        try:
            print('Recognizing speech...')
            query = listener.recognize_google(input_speech, language='en_gb') 
            print(f'The input speech was: {query}')
            

        except Exception as exception:
            print('I did not quite catch that')
            print(exception)

            return None;

        return query

def search_wikipedia(keyword=''):
    searchResults = wikipedia.search(keyword)
    if not searchResults:
        return 'No result received'
    try: 
        wikiPage = wikipedia.page(searchResults[0]) 
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']

def search_wolframalpha(keyword=''):
    response = wolframClient.query(keyword)
  

    # Query not resolved
    if response['@success'] == 'false':
        speak('I could not compute')
    # Query resolved
    else: 
        result = ''
        # Question
        pod0 = response['pod'][0]
        # May contain answer (Has highest confidence value) 
        # if it's primary or has the title of result or definition, then it's the official result
        pod1 = response['pod'][1]
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            # Get the result
            result = listOrDict(pod1['subpod'])
            # Remove bracketed section
            return result.split('(')[0]
        else:
            # Get the interpretation from pod0
            question = listOrDict(pod0['subpod'])
            # Remove bracketed section
            question = question.split('(')[0]
            # Could search wiki instead here? 
            return question

def query_openai(prompt="",model="GPT-3"):
    # Set your OpenAI API key 
    api_key=os.environ.get("OPENAI_API_KEY")
    openai.api_key = api_key

    

    # Set the API key for authentication

    # Temperature is a measure of randomness
    # Max_tokens is the number of tokens to generate
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()  # Return the generated text


# Main loop
if __name__ == '__main__': 
    speak('All systems nominal.', 120)
    query=''
    count=0

    while True: 
        count+=1 
        # Parse as a list
        # query = 'computer say hello'.split() 
        try:
            query = parseCommand().lower().split()  
        except: 
            speak('goodbye')
            break 
        

        if query[0] in activationWords and len(query) > 1:
            query.pop(0)

            # Set commands
        if query[0] == 'say':
            if 'hello' in query:
                speak('Greetings, all!')
            else:
                query.pop(0) # Remove 'say'
                speech = ' '.join(query) 
                speak(speech)

            # Query OpenAI
        if query[0] == 'insight' or query[0] =='inside' or 'chatgpt' in query or 'gpt' in query:
            query.pop(0) # Remove 'insight'  
            if 'chatgpt' in query:
                query.remove('chatgpt') 
            elif 'gpt' in query:
                query.remove('gpt')
            query = ' '.join(query) 
            try:
                speech = query_openai(query)
                speak("Ok")
                speak(speech) 
            except: 
                speak("plz set your OPENAI KEY variable ")


            # Navigation
        if query[0] == 'go' and query[1] == 'to' or query[0]=='search' and query[1]=='for' or query[0]=='open' :
            speak('Opening... ')
            # Assume the structure is activation word + go to, so let's remove the next two words
            query = ' '.join(query[2:])
            try:
                 webbrowser.open(query)
            except webbrowser.Error as e:
                print("Web browser error:", e)
            except Exception as e:
                print("An error occurred:", e)


            # Wikipedia
        if query[0] == 'wikipedia':
            
            query = ' '.join(query[1:])
            speak('Querying the universal databank')
            time.sleep(2) 
            
            speak(search_wikipedia(query),200) 
            engine.runAndWait()
 
                
            

            # Wolfram Alpha
        if query[0] == 'compute' or query[0] == 'computer':
            query = ' '.join(query[1:])
            try:
                result = search_wolframalpha(query)
                speak(result)
            except:
                speak('Unable to compute')

            # Note taking
        if query[0] == 'log' or query[0]=='note' or query[0] == 'write' or query[0]=='right':  
            speak('Ready to record your note')
            newNote = parseCommand().lower()
            now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            with open('note_%s.txt' % now, 'w') as newFile:
                newFile.write(now)
                newFile.write(' ')
                newFile.write(newNote)
                speak('Note written')
        if query[0]=='are' and query[1]=='you': 
            speak('cannot answer that' )  
        
        
        if query[0]=='play' and 'youtube' in query : 
            query.pop(0) 
            query.remove('youtube')
            kit.playonyt(query)
            
        if query[0]=='search' and 'youtube' in query: 
            query.pop(0) 
            if query[0]=='for':
                query.pop(0)
            if 'on youtube' in query: 
                query.remove('on youtube')
            else:
                query.remove('youtube') 
            kit.search(' '.join(query))               
        if query[0] == 'exit':
            speak('Goodbye') 
            break 
        if 'your' and 'name' in query: 
            speak('My name is Assistant')    
            
            
        
             