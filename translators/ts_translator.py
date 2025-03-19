import os
import re
import logging
import glob
from .base_translator import BaseTranslator

class TsTranslator(BaseTranslator):
    def __init__(self, config, translation_service):
        super().__init__(config, translation_service)
    
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
            content = self.parse_file(file_path)
            if not content:
                return False, "文件读取失败"
            
            # 更新进度
            if progress_callback:
                progress_callback(10, 1, 3, "正在读取文件...")
            
            # 检查是否取消
            if self.cancel_translation:
                return False, "翻译已取消"
            
            # 获取目标语言
            target_lang = self.config.get("target_lang", "英语")
            
            # 构建翻译提示
            prompt = f"""
            请将以下TypeScript/JavaScript语言文件翻译成{target_lang}。
            这是一个语言资源文件，只需要翻译字符串值，保持键名和文件结构不变。
            请确保翻译后的代码仍然是有效的TypeScript/JavaScript代码。
            
            原始文件内容:
            {content}
            """
            
            # 更新进度
            if progress_callback:
                progress_callback(30, 2, 3, "正在翻译文件...")
            
            # 检查是否取消
            if self.cancel_translation:
                return False, "翻译已取消"
            
            # 使用翻译服务翻译整个文件
            translated_content = self.translation_service.translate_text(prompt, target_lang)
            
            if not translated_content:
                return False, "翻译失败，请检查API设置"
            
            # 提取翻译后的代码部分（可能包含在代码块中）
            code_pattern = r'```(?:javascript|typescript|js|ts)?\s*([\s\S]*?)\s*```'
            code_match = re.search(code_pattern, translated_content)
            
            if code_match:
                translated_content = code_match.group(1).strip()
            else:
                # 尝试提取整个响应作为代码
                # 移除可能的解释性文本
                translated_content = re.sub(r'^.*?(?=export|module\.exports|const|let|var)', '', translated_content, flags=re.DOTALL)
                translated_content = re.sub(r'(?<=;)[\s\S]*$', '', translated_content)
            
            # 更新进度
            if progress_callback:
                progress_callback(80, 3, 3, "正在保存翻译结果...")
            
            # 检查是否取消
            if self.cancel_translation:
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
        # 查找所有匹配的文件
        search_pattern = os.path.join(folder_path, "**", filename_pattern)
        matching_files = glob.glob(search_pattern, recursive=True)
        
        if not matching_files:
            return False, f"在文件夹 {folder_path} 中未找到匹配 {filename_pattern} 的文件"
        
        total_files = len(matching_files)
        translated_files = 0
        failed_files = 0
        
        self.cancel_translation = False
        
        for i, file_path in enumerate(matching_files):
            # 检查是否取消
            if self.cancel_translation:
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