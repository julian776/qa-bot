"""
Language detection service using langdetect
"""
import logging
from typing import Optional
from langdetect import detect, DetectorFactory, LangDetectException

logger = logging.getLogger(__name__)

# Set seed for consistent results
DetectorFactory.seed = 0


class LanguageDetector:
    """Detect language of text (supports English and Spanish)"""

    SUPPORTED_LANGUAGES = {
        'en': 'english',
        'es': 'spanish'
    }

    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of text

        Args:
            text: Text to detect language from

        Returns:
            Language code ('en' or 'es') or None if detection fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for language detection")
            return None

        try:
            # Detect language
            detected_lang = detect(text)

            # Only return if it's one of our supported languages
            if detected_lang in self.SUPPORTED_LANGUAGES:
                logger.info(f"Detected language: {self.SUPPORTED_LANGUAGES[detected_lang]} ({detected_lang})")
                return detected_lang
            else:
                logger.warning(f"Detected unsupported language: {detected_lang}, defaulting to English")
                return 'en'  # Default to English

        except LangDetectException as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'  # Default to English on error

    def is_supported_language(self, lang_code: str) -> bool:
        """Check if language code is supported"""
        return lang_code in self.SUPPORTED_LANGUAGES

    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from code"""
        return self.SUPPORTED_LANGUAGES.get(lang_code, 'unknown')
