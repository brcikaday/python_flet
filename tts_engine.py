import pyttsx3
import threading
from typing import Callable, Optional

class TTSEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.is_speaking = False
        self.is_paused = False
        self.current_text = ""
        self.current_position = 0
        self.on_word_callback: Optional[Callable] = None
        
    def set_voice(self, voice_id: str):
        """Set the voice for TTS"""
        voices = self.engine.getProperty('voices')
        if voice_id == "male":
            # Try to find a male voice
            for voice in voices:
                if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    return
        elif voice_id == "female":
            # Try to find a female voice
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    return
        # Default voice
        if voices:
            self.engine.setProperty('voice', voices[0].id)
    
    def set_rate(self, rate: float):
        """Set speaking rate (0.5 to 2.0)"""
        # Convert to pyttsx3 rate (typically 100-300)
        pyttsx_rate = int(200 * rate)
        self.engine.setProperty('rate', pyttsx_rate)
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.engine.setProperty('volume', volume)
    
    def speak(self, text: str, on_word: Optional[Callable] = None):
        """Speak the given text"""
        if self.is_speaking:
            self.stop()
        
        self.current_text = text
        self.on_word_callback = on_word
        self.is_speaking = True
        self.is_paused = False
        
        def speak_thread():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                self.is_speaking = False
                self.is_paused = False
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
    
    def pause(self):
        """Pause speaking"""
        if self.is_speaking and not self.is_paused:
            self.engine.stop()
            self.is_paused = True
    
    def resume(self):
        """Resume speaking"""
        if self.is_paused:
            self.is_paused = False
            # Note: pyttsx3 doesn't support true pause/resume
            # This is a limitation of the library
    
    def stop(self):
        """Stop speaking"""
        if self.is_speaking:
            self.engine.stop()
            self.is_speaking = False
            self.is_paused = False
    
    def get_voices(self):
        """Get available voices"""
        voices = self.engine.getProperty('voices')
        return [(voice.id, voice.name) for voice in voices] if voices else []
