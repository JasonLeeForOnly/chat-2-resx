import os
import json
import logging

class Config:
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser("~"), ".resource_translator.json")
        self.default_config = {
            "api_type": "DeepLX",
            "deeplx_url": "",
            "chatgpt_base": "http://172.18.9.26:3000/api",
            "chatgpt_key": "",
            "chatgpt_model": "gemma3:27b",
            "target_lang": "英语",
            "enable_logging": False,
            "batch_size": 5,
            "system_prompt": (
                "你是一名经验丰富的翻译员，负责将指定文本翻译成目标语言，并确保译文准确、流畅且符合本地语言习惯。"
                "你的目标是提供自然、专业的翻译，忠实传达原文的意义和语气，同时适应仓储系统的行业特点和专业术语。"
                "请遵循以下翻译指南："
                "- 保持原意：准确传达原文的内容和意图，避免曲解或遗漏信息。"
                "- 提高可读性：减少冗长复杂的句子，避免生僻词，使表达清晰流畅。"
                "- 精准翻译：避免逐字直译，侧重于传达概念和意图，使译文自然易懂。"
                "- 本地化适配：结合目标语言的文化背景和表达习惯，适当调整措辞，使用符合仓储行业标准的术语。"
                "- 保持语气和风格：尽量还原原文的正式程度和表达方式。"
                "- 语法与规范：确保语法正确、拼写无误，标点符合目标语言的使用规范。"
                "- 在翻译仓储系统相关内容时，请特别注意行业术语，确保符合专业表达，贴合目标市场用户的阅读习惯。"
                "- 重要：最终只能返回一个翻译结果，不要返回任何其他内容！！！"
            ),
            "last_file_type": "RESX"  # 新增：上次使用的文件类型
        }
        self.config = self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.default_config.copy()
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            return self.default_config.copy()

    def save_config(self, config):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config(self.config)

    def get_all(self):
        return self.config.copy() 