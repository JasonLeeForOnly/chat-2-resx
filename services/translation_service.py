import logging
import abc

class TranslationService(abc.ABC):
    def __init__(self, config):
        self.config = config
        self.enable_logging = config.get("enable_logging", False)
        self.cancel_translation = False  # 添加取消标志

    def cancel(self):
        """取消翻译过程"""
        self.cancel_translation = True
        self.log_info("翻译已取消")
        
    def reset_cancel(self):
        """重置取消标志"""
        self.cancel_translation = False

    @abc.abstractmethod
    def translate_text(self, text, target_lang, system_prompt=None):
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

    def translate_text(self, prompt, target_lang, system_prompt=None):
        """
        翻译文本到目标语言
        
        Args:
            prompt (str): 要翻译的文本
            target_lang (str): 目标语言代码
            system_prompt (str, optional): 翻译器特定的系统提示
            
        Returns:
            str: 翻译后的文本
        """
        # 获取当前选择的翻译器
        translator = self.get_current_translator()
        
        # 获取用户配置的系统提示(如果有)
        user_system_prompt = self.config.get_config().get("system_prompt", "")
        
        # 合并系统提示
        combined_system_prompt = None
        if user_system_prompt and system_prompt:
            # 如果两者都存在，可以合并或作为两条消息处理
            combined_system_prompt = f"{user_system_prompt}\n\n{system_prompt}"
        elif user_system_prompt:
            combined_system_prompt = user_system_prompt
        elif system_prompt:
            combined_system_prompt = system_prompt
        
        # 调用翻译器的翻译方法，传入系统提示
        translated_text = translator.translate(prompt, target_lang, system_prompt=combined_system_prompt)
        
        return translated_text 