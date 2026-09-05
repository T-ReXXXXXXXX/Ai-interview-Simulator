import cv2
import numpy as np
from deepface import DeepFace


def analyze_emotion_from_image(image_array):
    """Analyze emotion from a single image array"""
    try:
        # Handle different image formats
        if isinstance(image_array, np.ndarray):
            # Ensure uint8 format
            if image_array.dtype != np.uint8:
                image_array = np.clip(image_array, 0, 255).astype(np.uint8)
            
            # Handle RGBA -> RGB conversion if needed
            if len(image_array.shape) == 3 and image_array.shape[2] == 4:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            
            # Analyze with DeepFace
            result = DeepFace.analyze(
                image_array,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            
            if result and len(result) > 0:
                return result[0]['dominant_emotion'], result[0]['emotion']
        
        return 'neutral', {}
    except Exception as e:
        print(f"Emotion detection error: {str(e)}")
        return 'neutral', {}


def calculate_emotion_metrics(emotion_scores_list):
    """
    Calculate overall emotion metrics from a list of emotion score dictionaries.
    Returns engagement, confidence, and stress scores as percentages (0-100).
    
    Args:
        emotion_scores_list: List of emotion dictionaries from emotion history
    
    Returns:
        dict with keys: engagement, confidence, stress
    """
    if not emotion_scores_list or len(emotion_scores_list) == 0:
        return {'engagement': 0, 'confidence': 0, 'stress': 0}
    
    # Aggregate emotion scores
    avg_emotions = {}
    emotion_keys = ['happy', 'neutral', 'sad', 'angry', 'fear', 'disgust', 'surprise']
    
    for key in emotion_keys:
        scores = [e.get(key, 0) for e in emotion_scores_list if isinstance(e, dict)]
        avg_emotions[key] = sum(scores) / len(scores) if scores else 0
    
    # Calculate metrics based on emotion values
    engagement = round(avg_emotions.get('happy', 0) + avg_emotions.get('surprise', 0), 1)
    confidence = round(avg_emotions.get('happy', 0) + avg_emotions.get('neutral', 0), 1)
    stress = round(avg_emotions.get('fear', 0) + avg_emotions.get('angry', 0), 1)
    
    return {
        'engagement': min(100, engagement),
        'confidence': min(100, confidence),
        'stress': min(100, stress),
        'raw_emotions': avg_emotions
    }


def record_and_get_emotion(duration=10):
    """Record audio for duration seconds and return transcription"""
    import speech_recognition as sr
    
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=duration)
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return "No speech detected. Please try again."
        except sr.UnknownValueError:
            return "Could not understand. Please speak clearly."
        except Exception as e:
            return f"Error: {str(e)}"