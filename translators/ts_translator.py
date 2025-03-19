import os
import re
import json
import logging
import glob
from .base_translator import BaseTranslator

class TsTranslator(BaseTranslator):
    def __init__(self, config, translation_service):
        super().__init__(config, translation_service)
        self.prompts = self._load_prompts()
    
    def _load_prompts(self):
        """加载系统提示词配置"""
        try:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            prompts_file = os.path.join(config_dir, 'prompts.json')
            
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            return prompts.get('ts_translator', {})
        except Exception as e:
            logging.error(f"加载提示词配置失败: {str(e)}")
            return {}
    
    def parse_file(self, file_path):
        """简单读取TS文件内容，不进行复杂解析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logging.error(f"读取TS文件出错: {str(e)}")
            return None
    
    def get_language_file_code(self, lang_name):
        """获取语言文件代码（小写）"""
        lang_codes = {
            "英语": "en",
            "简体中文": "zh-cn",
            "繁体中文": "zh-tw",
            "日语": "ja",
            "韩语": "ko",
            "德语": "de",
            "法语": "fr",
            "西班牙语": "es",
            "葡萄牙语": "pt",
            "意大利语": "it",
            "俄语": "ru",
            "荷兰语": "nl",
            "波兰语": "pl",
            "泰语": "th",
            "乌克兰语": "uk",
        }
        return lang_codes.get(lang_name, "en")
    
    def preview_translation(self, file_path):
        """预览翻译结果"""
        content = self.parse_file(file_path)
        if not content:
            return "文件读取失败"
        
        # 提取前200个字符进行预览
        preview_content = content[:200] + ("..." if len(content) > 200 else "")
        
        target_lang = self.config.get("target_lang", "英语")
        
        preview_text = f"文件内容预览:\n\n{preview_content}\n\n"
        preview_text += f"该文件将被整体翻译为{target_lang}，并保存为 {self.get_language_file_code(target_lang)}.ts"
        
        return preview_text
    
    def translate_file(self, file_path, output_path, progress_callback=None):
        """翻译TS文件并保存"""
        try:
            # 重置取消标志
            self.translation_service.reset_cancel()
            
            content = self.parse_file(file_path)
            if not content:
                return False, "文件读取失败"
            
            # 更新进度
            if progress_callback:
                progress_callback(10, 1, 3, "正在读取文件...")
            
            # 检查是否取消
            if self.translation_service.cancel_translation:
                return False, "翻译已取消"
            
            # 获取目标语言
            target_lang = self.config.get("target_lang", "英语")
            
            # 从配置加载系统提示词
            system_prompt = self.prompts.get('translate_file', {}).get('system_prompt', {}).get('zh', '')
            if system_prompt:
                system_prompt = system_prompt.replace('{target_lang}', target_lang)
            
            # 更新进度
            if progress_callback:
                progress_callback(30, 2, 3, "正在翻译文件...")
            
            # 检查是否取消
            if self.translation_service.cancel_translation:
                return False, "翻译已取消"
            
            # 使用翻译服务翻译整个文件
            translated_content = self.translation_service.translate_text(
                content, 
                target_lang,
                system_prompt=system_prompt
            )
            
            # 检查是否取消
            if self.translation_service.cancel_translation:
                return False, "翻译已取消"
                
            if not translated_content:
                return False, "翻译失败，请检查API设置"
            
            # 提取翻译后的代码部分（可能包含在代码块中）
            # 去掉包裹的 ```json 标记
            # translated_content = re.sub(r"^```json|```$", "", translated_content.strip(), flags=re.MULTILINE).strip()
            translated_content = re.sub(r"^```(json|typescript|ts|js|javascript|tex)|```$", "", translated_content.strip(), flags=re.MULTILINE).strip()

            # 更新进度
            if progress_callback:
                progress_callback(80, 3, 3, "正在保存翻译结果...")
            
            # 检查是否取消
            if self.translation_service.cancel_translation:
                return False, "翻译已取消"
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 写入翻译后的内容
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            # 更新进度
            if progress_callback:
                progress_callback(100, 3, 3, "翻译完成")
            
            return True, f"翻译完成!\n保存至: {output_path}"
            
        except Exception as e:
            logging.error(f"翻译过程中出现错误: {str(e)}")
            return False, f"翻译过程中出现错误: {str(e)}"
    
    def scan_folder(self, folder_path, filename_pattern, target_lang, progress_callback=None):
        """扫描文件夹并翻译所有匹配的文件"""
        # 重置取消标志
        self.translation_service.reset_cancel()
        
        # 查找所有匹配的文件
        search_pattern = os.path.join(folder_path, "**", filename_pattern)
        matching_files = glob.glob(search_pattern, recursive=True)
        
        if not matching_files:
            return False, f"在文件夹 {folder_path} 中未找到匹配 {filename_pattern} 的文件"
        
        total_files = len(matching_files)
        translated_files = 0
        failed_files = 0
        
        for i, file_path in enumerate(matching_files):
            # 检查是否取消
            if self.translation_service.cancel_translation:
                return False, "翻译已取消"
            
            # 生成输出文件路径
            dir_name = os.path.dirname(file_path)
            lang_code = self.get_language_file_code(target_lang)
            output_path = os.path.join(dir_name, f"{lang_code}.ts")
            
            # 更新总进度
            if progress_callback:
                file_progress = (i / total_files) * 100
                progress_callback(file_progress, i, total_files, f"正在翻译 {os.path.basename(file_path)}")
            
            # 翻译文件
            def file_progress_callback(progress, current, total, status=""):
                if progress_callback:
                    # 计算总体进度
                    overall_progress = ((i + progress/100) / total_files) * 100
                    progress_callback(overall_progress, i, total_files, f"正在翻译 {os.path.basename(file_path)} ({current}/{total}) {status}")
            
            success, message = self.translate_file(file_path, output_path, file_progress_callback)
            
            if success:
                translated_files += 1
            else:
                failed_files += 1
                logging.error(f"翻译文件 {file_path} 失败: {message}")
        
        return True, f"文件夹翻译完成!\n成功翻译: {translated_files} 个文件\n失败: {failed_files} 个文件"