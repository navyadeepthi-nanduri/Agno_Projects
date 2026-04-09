import speech_recognition as sr

def transcribe_audio(audio_file):
    if audio_file is None:
        return "No audio provided."

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data).strip()

        if not text:
            return "Sorry, I could not understand the audio."

        return text

    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except Exception as e:
        return f"Speech recognition error: {str(e)}"