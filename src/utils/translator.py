from typing import Optional
from deep_translator import GoogleTranslator


class Translator:
    """Utility for translating text from various languages to English"""

    def __init__(self):
        """Initialize the translator with Google Translate (free)"""
        self.translator = GoogleTranslator(source='auto', target='en')

    def translate_to_english(self, text: str, source_lang: str = 'auto') -> Optional[str]:
        """
        Translate text to English

        Args:
            text: Text to translate
            source_lang: Source language code (default 'auto' for auto-detection)
                        Common codes: 'zh-CN' (Chinese), 'de' (German),
                        'fr' (French), 'ru' (Russian), 'ar' (Arabic)

        Returns:
            Translated text in English, or original text if translation fails
        """
        if not text or not text.strip():
            return text

        try:
            # Update source language if specified
            if source_lang != self.translator.source:
                self.translator = GoogleTranslator(source=source_lang, target='en')

            # Translate text
            translated = self.translator.translate(text)
            return translated

        except Exception as e:
            print(f"  Translation error: {e}. Returning original text.")
            return text

    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text

        Args:
            text: Text to analyze

        Returns:
            Language code (e.g., 'en', 'zh-CN', 'de', 'fr')
        """
        try:
            from deep_translator import single_detection
            lang = single_detection(text, api_key=None)
            return lang
        except Exception as e:
            print(f"  Language detection error: {e}")
            return None

    def is_english(self, text: str) -> bool:
        """
        Check if text is in English

        Args:
            text: Text to check

        Returns:
            True if text is in English, False otherwise
        """
        if not text:
            return True

        lang = self.detect_language(text)
        return lang == 'en' if lang else True
