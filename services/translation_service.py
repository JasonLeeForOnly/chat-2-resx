import logging
import abc

class TranslationService(abc.ABC):
    def __init__(self, config):
        self.config = config
        self.enable_logging = config.get("enable_logging", False)

    @abc.abstractmethod
    def translate_text(self, text, target_lang):
        """翻译单个文本"""
        pass

    @abc.abstractmethod
    def batch_translate(self, texts_dict, target_lang):
        """批量翻译多个文本"""
        pass

    def log_info(self, message):
        if self.enable_logging:
            logging.info(message)

    def log_error(self, message):
        logging.error(message) 