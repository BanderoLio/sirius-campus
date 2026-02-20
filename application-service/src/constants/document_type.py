from typing import Final

DOCUMENT_TYPE_SIGNED_APPLICATION: Final[str] = "signed_application"
DOCUMENT_TYPE_PARENT_LETTER: Final[str] = "parent_letter"
DOCUMENT_TYPE_VOICE_MESSAGE: Final[str] = "voice_message"

DOCUMENT_TYPES: Final[frozenset[str]] = frozenset({
    DOCUMENT_TYPE_SIGNED_APPLICATION,
    DOCUMENT_TYPE_PARENT_LETTER,
    DOCUMENT_TYPE_VOICE_MESSAGE,
})

SCAN_ALLOWED_EXTENSIONS: Final[frozenset[str]] = frozenset({"pdf", "jpg", "jpeg", "png"})
VOICE_ALLOWED_EXTENSIONS: Final[frozenset[str]] = frozenset({"mp3", "m4a", "wav"})

MAX_SCAN_SIZE_BYTES: Final[int] = 10 * 1024 * 1024
MAX_VOICE_SIZE_BYTES: Final[int] = 5 * 1024 * 1024
