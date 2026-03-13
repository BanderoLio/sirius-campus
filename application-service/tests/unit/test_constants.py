from src.constants.document_type import (
    DOCUMENT_TYPE_SIGNED_APPLICATION,
    DOCUMENT_TYPE_PARENT_LETTER,
    DOCUMENT_TYPE_VOICE_MESSAGE,
    DOCUMENT_TYPES,
    SCAN_ALLOWED_EXTENSIONS,
    VOICE_ALLOWED_EXTENSIONS,
)


def test_document_types_contain_all_expected() -> None:
    assert DOCUMENT_TYPE_SIGNED_APPLICATION in DOCUMENT_TYPES
    assert DOCUMENT_TYPE_PARENT_LETTER in DOCUMENT_TYPES
    assert DOCUMENT_TYPE_VOICE_MESSAGE in DOCUMENT_TYPES
    assert len(DOCUMENT_TYPES) == 3


def test_scan_extensions() -> None:
    assert "pdf" in SCAN_ALLOWED_EXTENSIONS
    assert "jpg" in SCAN_ALLOWED_EXTENSIONS
    assert "png" in SCAN_ALLOWED_EXTENSIONS


def test_voice_extensions() -> None:
    assert "mp3" in VOICE_ALLOWED_EXTENSIONS
    assert "m4a" in VOICE_ALLOWED_EXTENSIONS
    assert "wav" in VOICE_ALLOWED_EXTENSIONS
