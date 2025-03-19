import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from datetime import datetime

from config import Config
from services.deeplx_service import DeepLXService
from services.chatgpt_service import ChatGPTService
from translators.resx_translator import ResxTranslator
from translators.ts_translator import TsTranslator
from ui.config_dialog import ConfigDialog
from ui.progress_dialog import ProgressDialog

class MainWindow:
    def __init__(self, master):
        self.master = master
        master.title("资源文件翻译工具")
        master.geometry("600x700")
        
        # 初始化配置
        self.config = Config()
        self.setup_logging()
        
        # 创建主框架
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件类型选择部分
        file_type_frame = ttk.LabelFrame(main_frame, text="文件类型", padding="5")
        file_type_frame.pack(fill=tk.X, pady=5)
        
        self.file_type = tk.StringVar(value=self.config.get("last_file_type", "RESX"))
        
        file_type_inner_frame = ttk.Frame(file_type_frame)
        file_type_inner_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(
            file_type_inner_frame, 
            text="RESX资源文件", 
            variable=self.file_type, 
            value="RESX",
            command=self.toggle_file_type
        ).pack(side=tk.LEFT, padx=20)
        
        ttk.Radiobutton(
            file_type_inner_frame, 
            text="TS资源文件", 
            variable=self.file_type, 
            value="TS",
            command=self.toggle_file_type
        ).pack(side=tk.LEFT, padx=20)
        
        # RESX文件选择部分
        self.resx_frame = ttk.LabelFrame(main_frame, text="RESX文件选择", padding="5")
        self.resx_frame.pack(fill=tk.X, pady=5)
        
        self.resx_file_path = tk.StringVar()
        ttk.Entry(self.resx_frame, textvariable=self.resx_file_path, width=50).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.resx_frame, text="浏览", command=self.browse_resx_file).grid(row=0, column=1, padx=5, pady=5)
        
        # TS文件选择部分
        self.ts_frame = ttk.LabelFrame(main_frame, text="TS文件选择", padding="5")
        
        # 文件夹选择
        folder_frame = ttk.Frame(self.ts_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(folder_frame, text="文件夹:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ts_folder_path = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.ts_folder_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(folder_frame, text="浏览", command=self.browse_ts_folder).grid(row=0, column=2, padx=5, pady=5)
        
        # 文件名模式
        pattern_frame = ttk.Frame(self.ts_frame)
        pattern_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pattern_frame, text="文件名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ts_filename = tk.StringVar(value="zh-cn.ts")
        ttk.Entry(pattern_frame, textvariable=self.ts_filename, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(pattern_frame, text="(例如: zh-cn.ts)").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # 翻译设置部分
        trans_frame = ttk.LabelFrame(main_frame, text="翻译设置", padding="5")
        trans_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(trans_frame, text="目标语言:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 目标语言选择
        self.target_lang = tk.StringVar(value=self.config.get("target_lang", "英语"))
        self.target_lang.trace_add("write", self.on_target_lang_change)  # 添加回调函数
        
        languages = ["英语", "简体中文", "繁体中文", "日语", "韩语", "德语", "法语", 
                    "西班牙语", "葡萄牙语", "意大利语", "俄语", "荷兰语", "波兰语", "泰语", "乌克兰语"]
        
        target_lang_combo = ttk.Combobox(
            trans_frame, 
            textvariable=self.target_lang,
            values=languages,
            width=10,
            state="readonly"
        )
        target_lang_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # API设置按钮
        ttk.Button(trans_frame, text="API设置", command=self.open_config_dialog).grid(row=0, column=2, padx=5, pady=5)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="翻译预览", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=10)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.preview_text, command=self.preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.config(yscrollcommand=scrollbar.set)
        
        # 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="预览翻译", command=self.preview_translation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="执行翻译", command=self.translate_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="退出", command=self.on_closing).pack(side=tk.RIGHT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)
        
        # 初始化界面
        self.toggle_file_type()
        
        # 设置关闭事件
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_logging(self):
        """设置日志"""
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
    
    def toggle_file_type(self):
        """切换文件类型界面"""
        file_type = self.file_type.get()
        self.config.set("last_file_type", file_type)
        
        if file_type == "RESX":
            self.resx_frame.pack(fill=tk.X, pady=5)
            self.ts_frame.pack_forget()
        else:  # TS
            self.resx_frame.pack_forget()
            self.ts_frame.pack(fill=tk.X, pady=5)
    
    def browse_resx_file(self):
        """浏览选择RESX文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("RESX文件", "*.resx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.resx_file_path.set(file_path)
            self.status_var.set(f"已选择文件: {os.path.basename(file_path)}")
    
    def browse_ts_folder(self):
        """浏览选择TS文件夹"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.ts_folder_path.set(folder_path)
            self.status_var.set(f"已选择文件夹: {folder_path}")
    
    def open_config_dialog(self):
        """打开配置对话框"""
        config_dialog = ConfigDialog(self.master, self.config)
        new_config = config_dialog.show()
        
        if new_config:
            # 更新配置
            for key, value in new_config.items():
                self.config.set(key, value)
            
            self.status_var.set("配置已更新")
    
    def get_translation_service(self):
        """获取翻译服务"""
        api_type = self.config.get("api_type", "DeepLX")
        
        if api_type == "DeepLX":
            return DeepLXService(self.config)
        else:  # ChatGPT
            return ChatGPTService(self.config)
    
    def get_translator(self, file_type):
        """获取翻译器实例"""
        # 根据配置创建翻译服务
        api_type = self.config.get("api_type", "DeepLX")
        
        if api_type == "DeepLX":
            translation_service = DeepLXService(self.config)
        else:  # ChatGPT
            translation_service = ChatGPTService(self.config)
        
        # 创建翻译器
        if file_type == "RESX":
            return ResxTranslator(self.config, translation_service)
        else:  # TS
            return TsTranslator(self.config, translation_service)
    
    def preview_translation(self):
        """预览翻译"""
        file_type = self.file_type.get()
        translator = self.get_translator(file_type)
        
        self.preview_text.delete(1.0, tk.END)
        self.status_var.set("正在预览翻译...")
        self.master.update()
        
        try:
            if file_type == "RESX":
                file_path = self.resx_file_path.get()
                if not file_path:
                    messagebox.showwarning("警告", "请先选择一个RESX文件")
                    self.status_var.set("就绪")
                    return
                
                preview_result = translator.preview_translation(file_path)
                self.preview_text.insert(tk.END, preview_result)
            else:  # TS
                folder_path = self.ts_folder_path.get()
                filename = self.ts_filename.get()
                
                if not folder_path:
                    messagebox.showwarning("警告", "请先选择一个文件夹")
                    self.status_var.set("就绪")
                    return
                
                if not filename:
                    messagebox.showwarning("警告", "请输入要查找的文件名")
                    self.status_var.set("就绪")
                    return
                
                # 查找匹配的文件
                import glob
                search_pattern = os.path.join(folder_path, "**", filename)
                matching_files = glob.glob(search_pattern, recursive=True)
                
                if not matching_files:
                    self.preview_text.insert(tk.END, f"在文件夹 {folder_path} 中未找到匹配 {filename} 的文件")
                    self.status_var.set("预览完成")
                    return
                
                # 预览第一个匹配的文件
                preview_result = translator.preview_translation(matching_files[0])
                
                self.preview_text.insert(tk.END, f"找到 {len(matching_files)} 个匹配的文件，预览第一个:\n")
                self.preview_text.insert(tk.END, f"文件: {matching_files[0]}\n\n")
                self.preview_text.insert(tk.END, preview_result)
            
            self.status_var.set("预览完成")
        except Exception as e:
            self.preview_text.insert(tk.END, f"预览过程中出现错误: {str(e)}")
            self.status_var.set("预览失败")
            logging.error(f"预览翻译出错: {str(e)}")
    
    def translate_file(self):
        """执行翻译"""
        file_type = self.file_type.get()
        translator = self.get_translator(file_type)
        target_lang = self.target_lang.get()
        
        try:
            if file_type == "RESX":
                file_path = self.resx_file_path.get()
                if not file_path:
                    messagebox.showwarning("警告", "请先选择一个RESX文件")
                    return
                
                # 确认是否继续
                if not messagebox.askyesno("确认", "确定要执行翻译并保存文件吗?"):
                    return
                
                # 创建输出文件路径
                file_dir, file_name = os.path.split(file_path)
                name, ext = os.path.splitext(file_name)
                lang_code = translator.get_language_code(target_lang)
                default_output_path = os.path.join(file_dir, f"{name}.{lang_code}{ext}")
                
                # 让用户选择保存位置和文件名
                output_path = filedialog.asksaveasfilename(
                    initialdir=file_dir,
                    initialfile=f"{name}.{lang_code}{ext}",
                    defaultextension=ext,
                    filetypes=[("RESX文件", "*.resx"), ("所有文件", "*.*")]
                )
                
                if not output_path:  # 用户取消了保存对话框
                    return
                
                # 显示进度对话框
                progress_dialog = ProgressDialog(self.master, "翻译进度")
                progress_dialog.set_cancel_callback(translator.cancel)
                
                # 执行翻译
                def translate_thread():
                    try:
                        success, message = translator.translate_file(
                            file_path, 
                            output_path, 
                            progress_dialog.update_progress
                        )
                        
                        # 在主线程中更新UI
                        self.master.after(0, lambda: self.handle_translation_result(success, message, progress_dialog))
                    except Exception as e:
                        self.master.after(0, lambda: self.handle_translation_error(str(e), progress_dialog))
                
                import threading
                thread = threading.Thread(target=translate_thread)
                thread.daemon = True
                thread.start()
                
            else:  # TS
                folder_path = self.ts_folder_path.get()
                filename = self.ts_filename.get()
                
                if not folder_path:
                    messagebox.showwarning("警告", "请先选择一个文件夹")
                    return
                
                if not filename:
                    messagebox.showwarning("警告", "请输入要查找的文件名")
                    return
                
                # 确认是否继续
                if not messagebox.askyesno("确认", f"确定要扫描文件夹 {folder_path} 并翻译所有匹配 {filename} 的文件吗?"):
                    return
                
                # 显示进度对话框
                progress_dialog = ProgressDialog(self.master, "翻译进度")
                progress_dialog.set_cancel_callback(translator.cancel)
                
                # 执行翻译
                def translate_thread():
                    try:
                        success, message = translator.scan_folder(
                            folder_path, 
                            filename, 
                            target_lang, 
                            progress_dialog.update_progress
                        )
                        
                        # 在主线程中更新UI
                        self.master.after(0, lambda: self.handle_translation_result(success, message, progress_dialog))
                    except Exception as e:
                        self.master.after(0, lambda: self.handle_translation_error(str(e), progress_dialog))
                
                import threading
                thread = threading.Thread(target=translate_thread)
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            messagebox.showerror("错误", f"翻译过程中出现错误: {str(e)}")
            self.status_var.set("翻译失败")
            logging.error(f"翻译出错: {str(e)}")
    
    def handle_translation_result(self, success, message, progress_dialog):
        """处理翻译结果"""
        progress_dialog.close()
        
        if success:
            messagebox.showinfo("成功", message)
            self.status_var.set("翻译完成")
        else:
            messagebox.showwarning("警告", message)
            self.status_var.set("翻译未完成")
    
    def handle_translation_error(self, error_message, progress_dialog):
        """处理翻译错误"""
        progress_dialog.close()
        messagebox.showerror("错误", f"翻译过程中出现错误: {error_message}")
        self.status_var.set("翻译失败")
    
    def on_closing(self):
        """关闭窗口"""
        if messagebox.askokcancel("退出", "确定要退出吗?"):
            self.master.destroy()
    
    def on_target_lang_change(self, *args):
        """当目标语言改变时自动保存配置"""
        selected_lang = self.target_lang.get()
        self.config.set("target_lang", selected_lang)
        self.status_var.set(f"目标语言已设置为: {selected_lang}") 