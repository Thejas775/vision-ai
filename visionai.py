import os
import subprocess
import speech_recognition as sr
from gtts import gTTS
import firebase_admin
from firebase_admin import credentials, storage
import replicate
from time import sleep

cred = credentials.Certificate("glasses.json")#replace with your own
firebase_admin.initialize_app(cred, {"storageBucket": "glasses-68bfa.appspot.com"})

def upload_image_to_firebase(image_path, destination_path):
    #for uploading image to firebase
    bucket = storage.bucket()

    blob = bucket.blob(destination_path)
    blob.upload_from_filename(image_path)


def get_firebase_image_url(image_path):
    bucket = storage.bucket()
    blob = bucket.blob(image_path)
    #for firebase url calling
    return "https://firebasestorage.googleapis.com/v0/b/glasses-68bfa.appspot.com/o/images%2Fcaptured_image.png?alt=media&token=2f619167-527e-4964-971c-278df8e259bb"


def record_audio():
    #for recording audio
    r = sr.Recognizer()
    print("Before Recording")
    with sr.Microphone() as source:
        print("Say something...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=5)
    print("After Recording")


    try:
        text = r.recognize_google(audio)
        print(text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def text_to_speech(text):
    #using google text to speech recognition
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    sleep(2)
    subprocess.run(["xdg-open","output.mp3"])

def call_api_with_firebase(prompt, image_url):
    #calling llava model
    output = replicate.run(
        "yorickvp/llava-13b:e272157381e2a3bf12df3a8edd1f38d1dbd736bbb7437277c8b34175f8fce358",
        input={"image": image_url, "prompt": prompt},
    )
    stri = ""

    for item in output:
        stri+=item
    text_to_speech(stri)

def capture_image(file_path='captured_image.png'):
    try:
        subprocess.run(['libcamera-still', '-e', 'png', '-o', file_path], check=True)
        print(f"Image captured and saved to {file_path}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    while True:
        command = record_audio()
        if command and ("hey vision" in command.lower() or "hello vision" in command.lower() or "vision" in command.lower()):
            print("Capturing image...")
            subprocess.run(["xdg-open","CapturingImage.mp3"])
            capture_image()
            print("Recording prompt...")
            subprocess.run(["xdg-open","RecordingPrompt.mp3"])
            sleep(1)
            prompt_text = record_audio()

            print("Uploading image to Firebase...")
            upload_image_to_firebase('captured_image.png', 'images/captured_image.png')
            firebase_image_url = get_firebase_image_url('images/captured_image.png')
            print("Deleting captured image...")
            os.remove('captured_image.png')
            print("Calling API with Firebase image URL...")
            call_api_with_firebase(prompt_text, firebase_image_url)
            print("Converting API output to speech...")
            sleep(2)  
