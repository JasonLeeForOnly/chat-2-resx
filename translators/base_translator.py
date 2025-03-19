import abc
import logging
import os
from datetime import datetime

class BaseTranslator(abc.ABC):
    def __init__(self, config, translation_service):
        self.config = config
        self.translation_service = translation_service
        self.setup_logging()
        self.cancel_translation = False
        
    def setup_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        log_file = os.path.join('logs', f'translator_{datetime.now().strftime("%Y%m%d")}.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    @abc.abstractmethod
    def parse_file(self, file_path):
        """解析文件内容"""
        pass
    
    @abc.abstractmethod
    def preview_translation(self, file_path):
        """预览翻译结果"""
        pass
    
    @abc.abstractmethod
    def translate_file(self, file_path, output_path, progress_callback=None):
        """翻译文件并保存"""
        pass
    
    def cancel(self):
        """取消翻译过程"""
        self.cancel_translation = True
    
    def get_language_code(self, lang_name):
        """获取语言代码"""
        languages = {
            "英语": "EN",
            "简体中文": "ZH",
            "繁体中文": "ZH-TW",
            "日语": "JA",
            "韩语": "KO",
            "德语": "DE",
            "法语": "FR",
            "西班牙语": "ES",
            "葡萄牙语": "PT",
            "意大利语": "IT",
            "俄语": "RU",
            "荷兰语": "NL",
            "波兰语": "PL",
            "泰语": "TH",
            "乌克兰语": "UK",
        }
        return languages.get(lang_name, "EN") 