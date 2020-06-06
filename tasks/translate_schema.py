from googletrans import Translator, LANGCODES, LANGUAGES
from typing import Dict
from pandas import DataFrame
from datenguidepy.query_execution import StatisticsSchemaJsonMetaDataProvider
from datenguidepy.translation import TranslationProvider
import re
import os
import time
import json

sleep_duration_between_requests_in_seconds = 2


class _GoogleTranslationProvider(TranslationProvider):
    def __init__(self):
        self.translation_client: Translator = Translator()
        self.translation_cache: Dict[str, Dict[str, str]] = dict()
        self.hyphenated_linebreak_regex = re.compile(r"\s*-\n\s*")
        self.linebreak_in_the_midst_of_text_regex = re.compile(r"\n[ ]*(\S+)")
        self.valid_languages = list(LANGCODES.keys()) + list(LANGUAGES.keys())

    def translate_from_german(self, source_text, target_language):
        if target_language not in self.translation_cache:
            self.translation_cache[target_language] = dict()
        if source_text not in self.translation_cache[target_language]:
            normalized_source_text = self.normalize_source_text(source_text)
            translation_result = self.translation_client.translate(
                normalized_source_text, src="de", dest=target_language
            )
            self.translation_cache[target_language][
                source_text
            ] = translation_result.text

        return self.translation_cache[target_language][source_text]

    def translate_data_frame_from_german(self, data_frame: DataFrame, target_language):
        for column in data_frame.columns:
            for source_text in data_frame[column].unique():
                self.translate_from_german(source_text, target_language)
        data_frame.replace(self.translation_cache[target_language], inplace=True)

    def is_valid_language_code(self, language_code):
        return language_code in self.valid_languages

    def get_valid_language_codes(self):
        return self.valid_languages

    def normalize_source_text(self, source_text):
        substitution_string = re.sub(self.hyphenated_linebreak_regex, "", source_text)
        return re.sub(
            self.linebreak_in_the_midst_of_text_regex,
            " \g<1>",  # noqa: W605
            substitution_string,
        )


def translate_schema_to_target_language(
    target_language: str, translation_provider: TranslationProvider
):
    metadata_provider = StatisticsSchemaJsonMetaDataProvider()
    statistic_descriptions = metadata_provider.get_stat_descriptions()
    translation_dictionary: Dict = dict()

    for source_texts in statistic_descriptions.values():
        for source_text in source_texts:
            if source_text not in translation_dictionary:
                translated_text = translation_provider.translate_from_german(
                    source_text, target_language
                )
                translation_dictionary[source_text] = translated_text
                time.sleep(sleep_duration_between_requests_in_seconds)

    return {target_language: translation_dictionary}


def save_translated_schema(schema):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(curr_dir, "package_data")
    translation_json_path = os.path.join(data_dir, "translated_schema.json")
    with open(translation_json_path, "w") as translation_file:
        translation_file.write(json.dumps(schema))


if __name__ == "__main__":
    english_schema = translate_schema_to_target_language(
        "en", _GoogleTranslationProvider()
    )
    save_translated_schema(english_schema)
