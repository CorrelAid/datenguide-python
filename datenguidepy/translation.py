from typing import Dict

from abc import abstractmethod, ABC
from pandas import DataFrame
import json
import os


class TranslationProvider(ABC):
    @abstractmethod
    def translate_data_frame_from_german(
        self, data_frame: DataFrame, target_language: str
    ):
        pass

    @abstractmethod
    def translate_from_german(self, source_text: str, target_language: str):
        pass

    @abstractmethod
    def is_valid_language_code(self, target_language: str):
        pass

    @abstractmethod
    def get_valid_language_codes(self):
        pass


class SchemaTranslationProvider(TranslationProvider):
    def __init__(self):
        self.translated_schema: Dict = self.get_translated_schema_from_file()

    @staticmethod
    def get_translated_schema_from_file():
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(curr_dir, "package_data")
        translation_json_path = os.path.join(data_dir, "translated_schema.json")
        with open(translation_json_path) as translation_file:
            translation_schema = json.loads(translation_file.read())
        return translation_schema

    def translate_data_frame_from_german(
        self, data_frame: DataFrame, target_language: str
    ):
        data_frame.replace(self.translated_schema[target_language], inplace=True)

    def translate_from_german(self, source_text: str, target_language: str):
        language_specific_schema = self.translated_schema[target_language]
        if source_text in language_specific_schema:
            return language_specific_schema[source_text]
        else:
            return source_text

    def is_valid_language_code(self, target_language: str):
        return target_language in self.get_valid_language_codes()

    def get_valid_language_codes(self):
        return list(self.translated_schema.keys())


DEFAULT_TRANSLATION_PROVIDER = SchemaTranslationProvider()
