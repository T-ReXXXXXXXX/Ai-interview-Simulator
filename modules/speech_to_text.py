import speech_recognition as sr

def record_and_transcribe(duration=60):
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 5      # wait 5 seconds of silence before stopping
    recognizer.non_speaking_duration = 5 # also set non-speaking duration to 5s

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(
                source,
                timeout=10,            # wait max 10s for speech to START
                phrase_time_limit=duration  # max 60s total recording
            )
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return "No speech detected. Please try again."
        except sr.UnknownValueError:
            return "Could not understand. Please speak clearly."
        except sr.RequestError:
            return "Internet connection error."
        except Exception as e:
            return f"Error: {str(e)}"