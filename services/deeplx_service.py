import requests
from .translation_service import TranslationService

class DeepLXService(TranslationService):
    def __init__(self, config):
        super().__init__(config)
        self.api_url = config.get("deeplx_url", "")

    def translate_text(self, text, target_lang):
        if not text.strip():
            return ""
            
        if not self.api_url:
            self.log_error("DeepLX API URL未设置")
            return None
            
        try:
            payload = {
                "text": text,
                "source_lang": "auto",
                "target_lang": target_lang
            }
            
            self.log_info(f"DeepLX请求: URL={self.api_url}, Payload={payload}")
                
            response = requests.post(self.api_url + "/translate", json=payload)
            response.raise_for_status()
            result = response.json()
            
            self.log_info(f"DeepLX响应: {result}")
                
            return result.get("data", "")
        except Exception as e:
            error_msg = f"DeepLX翻译过程中出现错误: {str(e)}"
            self.log_error(error_msg)
            return None

    def batch_translate(self, texts_dict, target_lang):
        """批量翻译多个文本（DeepLX不支持批量，逐个翻译）"""
        result = {}
        for key, text in texts_dict.items():
            translated = self.translate_text(text, target_lang)
            if translated:
                result[key] = translated
        return result 