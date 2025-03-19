import requests
import json
import re
import threading
from .translation_service import TranslationService

class ChatGPTService(TranslationService):
    def __init__(self, config):
        super().__init__(config)
        self.api_base = config.get("chatgpt_base", "")
        self.api_key = config.get("chatgpt_key", "")
        self.model_name = config.get("chatgpt_model", "")
        self.system_prompt = config.get("system_prompt", "")
        
        # 去除API URL末尾的斜杠
        if self.api_base.endswith('/'):
            self.api_base = self.api_base[:-1]

    def translate_text(self, text, target_lang, system_prompt=None):
        if not text.strip():
            return ""
            
        if not self.api_base or not self.api_key or not self.model_name:
            self.log_error("ChatGPT API信息不完整")
            return None
        
        try:
            # 检查是否已取消
            if self.cancel_translation:
                self.log_info("翻译已取消")
                return None
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            messages = []
            # 添加系统提示词
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if self.system_prompt.strip():
                messages.append({"role": "system", "content": self.system_prompt})
                
            prompt = f"请将以下文本翻译成{target_lang}：\n\n{text}"
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            # 使用线程本地日志记录，避免多线程日志混乱
            thread_id = threading.get_ident()
            
            # 记录请求信息时隐藏API key
            if self.enable_logging:
                safe_headers = headers.copy()
                safe_headers["Authorization"] = "Bearer ********"
                self.log_info(f"线程 {thread_id} - ChatGPT请求: URL={self.api_base}/chat/completions, Headers={safe_headers}, Payload={payload}")
            
            # 添加超时和取消检查
            timeout = 60  # 设置60秒超时
            
            # 使用带超时的请求
            response = requests.post(
                f"{self.api_base}/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=timeout
            )
            
            # 再次检查是否已取消
            if self.cancel_translation:
                self.log_info("翻译已取消")
                return None
            
            response.raise_for_status()
            result = response.json()
            
            if self.enable_logging:
                self.log_info(f"线程 {thread_id} - ChatGPT响应: {result}")
            
            # 最后一次检查是否已取消
            if self.cancel_translation:
                self.log_info("翻译已取消")
                return None
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return None
        except requests.exceptions.Timeout:
            self.log_error(f"线程 {thread_id} - ChatGPT请求超时")
            return None
        except Exception as e:
            error_msg = f"线程 {thread_id} - ChatGPT翻译过程中出现错误: {str(e)}"
            self.log_error(error_msg)
            return None

    def batch_translate(self, texts_dict, target_lang):
        """批量翻译多个文本"""
        if not texts_dict:
            return {}
            
        if not self.api_base or not self.api_key or not self.model_name:
            self.log_error("ChatGPT API信息不完整")
            return {}
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 构建JSON格式的文本列表
            texts_json = json.dumps(texts_dict, ensure_ascii=False)
            
            messages = []
            # 添加系统提示词
            if self.system_prompt.strip():
                messages.append({"role": "system", "content": self.system_prompt})
            
            prompt = (
                f"请将以下JSON格式的文本翻译成{target_lang}。\n"
                f"JSON中的键是文本ID，值是需要翻译的文本。\n"
                f"请保持JSON格式不变，只翻译值部分，不要翻译键。\n"
                f"请直接返回翻译后的JSON，不要添加任何解释或其他内容。\n\n"
                f"{texts_json}"
            )
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 4000  # 增加token限制以处理批量文本
            }
            
            thread_id = threading.get_ident()
            
            if self.enable_logging:
                # 记录请求信息时隐藏API key
                safe_headers = headers.copy()
                safe_headers["Authorization"] = "Bearer ********"
                self.log_info(f"批量翻译 - ChatGPT请求: URL={self.api_base}/chat/completions, Headers={safe_headers}, Payload={payload}")
            
            response = requests.post(f"{self.api_base}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if self.enable_logging:
                self.log_info(f"批量翻译 - ChatGPT响应: {result}")
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"].strip()
                
                # 尝试从返回内容中提取JSON
                try:
                    # 查找JSON内容（可能被包裹在代码块中）
                    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        # 如果没有代码块，尝试直接解析整个内容
                        json_str = content
                    
                    translated_dict = json.loads(json_str)
                    return translated_dict
                except json.JSONDecodeError as e:
                    self.log_error(f"解析JSON响应失败: {e}, 响应内容: {content}")
                    return {}
            else:
                return {}
        except Exception as e:
            error_msg = f"批量翻译过程中出现错误: {str(e)}"
            self.log_error(error_msg)
            return {}

    def translate_with_chatgpt(self, text, target_lang, system_prompt=None):
        """
        使用ChatGPT翻译文本
        
        Args:
            text (str): 要翻译的文本
            target_lang (str): 目标语言代码
            system_prompt (str, optional): 用于翻译的系统提示
            
        Returns:
            str: 翻译后的文本
        """
        # 构建消息列表
        messages = []
        
        # 添加系统提示(如果有)
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加用户消息
        messages.append({"role": "user", "content": f"请将以下文本翻译成{target_lang}:\n\n{text}"})
        
        # 调用ChatGPT API
        # ... 现有代码 ...
        
        return translated_text

    def translate_with_chatgpt(self, text, target_lang, system_prompt=None):
        """
        使用ChatGPT翻译文本
        
        Args:
            text (str): 要翻译的文本
            target_lang (str): 目标语言代码
            system_prompt (str, optional): 用于翻译的系统提示
            
        Returns:
            str: 翻译后的文本
        """
        # 构建消息列表
        messages = []
        
        # 添加系统提示(如果有)
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加用户消息
        messages.append({"role": "user", "content": f"请将以下文本翻译成{target_lang}:\n\n{text}"})
        
        # 调用ChatGPT API
        # ... 现有代码 ...
        
        return translated_text 