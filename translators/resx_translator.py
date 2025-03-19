import os
import xml.etree.ElementTree as ET
import random
from .base_translator import BaseTranslator

class ResxTranslator(BaseTranslator):
    def __init__(self, config, translation_service):
        super().__init__(config, translation_service)
    
    def parse_file(self, file_path):
        try:
            # 读取原始XML以保留格式
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用ElementTree解析
            tree = ET.parse(file_path)
            root = tree.getroot()
            return root, content
        except Exception as e:
            logging.error(f"解析XML文件出错: {str(e)}")
            return None, None
    
    def preview_translation(self, file_path):
        root, _ = self.parse_file(file_path)
        if not root:
            return "文件解析失败"
            
        preview_text = ""
        
        # 随机选择几个条目进行预览
        data_nodes = root.findall(".//data")
        preview_count = min(1, len(data_nodes))
        
        if preview_count == 0:
            return "未找到可翻译的内容"
            
        preview_text += f"从{len(data_nodes)}个条目中随机选择{preview_count}个进行预览:\n\n"
        
        sample_nodes = random.sample(data_nodes, preview_count)
        target_lang = self.config.get("target_lang", "英语")
        
        for i, node in enumerate(sample_nodes):
            name = node.get('name', '')
            value_node = node.find('value')
            if value_node is not None and value_node.text:
                original = value_node.text
                translation = self.translation_service.translate_text(original, target_lang)
                
                preview_text += f"{i+1}. {name}\n"
                preview_text += f"   原文: {original}\n"
                if translation:
                    preview_text += f"   译文: {translation}\n\n"
                else:
                    preview_text += f"   译文: [翻译失败]\n\n"
        
        return preview_text
    
    def translate_file(self, file_path, output_path, progress_callback=None):
        root, _ = self.parse_file(file_path)
        if not root:
            return False, "文件解析失败"
            
        # 翻译所有data/value节点
        data_nodes = root.findall(".//data")
        total = len(data_nodes)
        translated = 0
        failed = 0
        
        self.cancel_translation = False
        
        # 确定使用哪种翻译方法
        api_type = self.config.get("api_type", "DeepLX")
        target_lang = self.config.get("target_lang", "英语")
        
        try:
            if api_type == "DeepLX":
                # 逐个翻译所有节点
                for i, node in enumerate(data_nodes):
                    # 检查是否取消
                    if self.cancel_translation:
                        return False, "翻译已取消"
                        
                    value_node = node.find('value')
                    if value_node is not None and value_node.text:
                        original = value_node.text
                        translation = self.translation_service.translate_text(original, target_lang)
                        
                        if translation:
                            value_node.text = translation
                            translated += 1
                        else:
                            failed += 1
                    
                    # 更新进度
                    if progress_callback:
                        progress = (i + 1) / total * 100
                        progress_callback(progress, i+1, total)
            else:  # ChatGPT批量翻译
                batch_size = self.config.get("batch_size", 5)
                
                # 将节点分成批次
                batches = [data_nodes[i:i+batch_size] for i in range(0, len(data_nodes), batch_size)]
                
                processed = 0
                for batch_idx, batch in enumerate(batches):
                    # 检查是否取消
                    if self.cancel_translation:
                        return False, "翻译已取消"
                    
                    # 收集这个批次中需要翻译的文本
                    texts_to_translate = {}
                    for i, node in enumerate(batch):
                        value_node = node.find('value')
                        if value_node is not None and value_node.text:
                            # 使用节点名称作为ID
                            node_id = node.get('name', f"item_{batch_idx}_{i}")
                            texts_to_translate[node_id] = value_node.text
                    
                    # 批量翻译
                    if texts_to_translate:
                        translated_texts = self.translation_service.batch_translate(texts_to_translate, target_lang)
                        
                        # 将翻译结果写回XML
                        for node in batch:
                            node_id = node.get('name')
                            value_node = node.find('value')
                            
                            if node_id in translated_texts and value_node is not None:
                                value_node.text = translated_texts[node_id]
                                translated += 1
                            else:
                                failed += 1
                    
                    # 更新进度
                    processed += len(batch)
                    if progress_callback:
                        progress = processed / total * 100
                        progress_callback(progress, processed, total)
            
            # 写入新文件
            tree = ET.ElementTree(root)
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            
            return True, f"翻译完成!\n成功翻译: {translated}\n失败: {failed}\n保存至: {output_path}"
            
        except Exception as e:
            logging.error(f"翻译过程中出现错误: {str(e)}")
            return False, f"翻译过程中出现错误: {str(e)}" 