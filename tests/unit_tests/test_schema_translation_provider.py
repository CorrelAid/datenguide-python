from datenguidepy.translation import SchemaTranslationProvider


def test_translation_for_schema_input():
    source_text = "Viehbestand"
    expected_translation = "livestock"
    actual_translation = SchemaTranslationProvider().translate_from_german(
        source_text, "en"
    )
    assert actual_translation == expected_translation


def test_valid_language_codes_not_empty():
    assert len(SchemaTranslationProvider().get_valid_language_codes()) != 0


def test_valid_language_code():
    assert SchemaTranslationProvider().is_valid_language_code("en") is True
