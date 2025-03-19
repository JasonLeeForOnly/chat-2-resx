import tkinter as tk
from tkinter import ttk

class ConfigDialog:
    def __init__(self, parent, config):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("配置")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        self.config = config
        self.result = None
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API设置选项卡
        self.api_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.api_frame, text="API设置")
        
        # 高级设置选项卡
        self.advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_frame, text="高级设置")
        
        # 创建API设置界面
        self.create_api_settings()
        
        # 创建高级设置界面
        self.create_advanced_settings()
        
        # 底部按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="保存", command=self.save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.RIGHT, padx=5)
    
    def create_api_settings(self):
        """创建API设置界面"""
        # API类型选择
        ttk.Label(self.api_frame, text="API类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.api_type = tk.StringVar(value=self.config.get("api_type", "DeepLX"))
        api_type_frame = ttk.Frame(self.api_frame)
        api_type_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(
            api_type_frame, 
            text="DeepLX", 
            variable=self.api_type, 
            value="DeepLX", 
            command=self.toggle_api_fields
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            api_type_frame, 
            text="ChatGPT", 
            variable=self.api_type, 
            value="ChatGPT", 
            command=self.toggle_api_fields
        ).pack(side=tk.LEFT, padx=5)
        
        # DeepLX设置
        self.deeplx_frame = ttk.LabelFrame(self.api_frame, text="DeepLX设置", padding=10)
        self.deeplx_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(self.deeplx_frame, text="API URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.deeplx_url = tk.StringVar(value=self.config.get("deeplx_url", ""))
        ttk.Entry(self.deeplx_frame, textvariable=self.deeplx_url, width=50).grid(row=0, column=1, padx=5, pady=5)
        
        # ChatGPT设置
        self.chatgpt_frame = ttk.LabelFrame(self.api_frame, text="ChatGPT设置", padding=10)
        self.chatgpt_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(self.chatgpt_frame, text="API Base URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.chatgpt_base = tk.StringVar(value=self.config.get("chatgpt_base", ""))
        ttk.Entry(self.chatgpt_frame, textvariable=self.chatgpt_base, width=50).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.chatgpt_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.chatgpt_key = tk.StringVar(value=self.config.get("chatgpt_key", ""))
        ttk.Entry(self.chatgpt_frame, textvariable=self.chatgpt_key, width=50, show="*").grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.chatgpt_frame, text="模型名称:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.chatgpt_model = tk.StringVar(value=self.config.get("chatgpt_model", ""))
        ttk.Entry(self.chatgpt_frame, textvariable=self.chatgpt_model, width=50).grid(row=2, column=1, padx=5, pady=5)
        
        # 系统提示词
        ttk.Label(self.chatgpt_frame, text="系统提示词:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        prompt_frame = ttk.Frame(self.chatgpt_frame)
        prompt_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.system_prompt = tk.StringVar(value=self.config.get("system_prompt", ""))
        self.prompt_button = ttk.Button(prompt_frame, text="编辑", command=self.edit_system_prompt)
        self.prompt_button.pack(side=tk.LEFT)
        
        # 初始化界面
        self.toggle_api_fields()
    
    def create_advanced_settings(self):
        """创建高级设置界面"""
        # 批处理设置
        ttk.Label(self.advanced_frame, text="批处理大小:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.batch_size = tk.IntVar(value=self.config.get("batch_size", 5))
        ttk.Spinbox(
            self.advanced_frame, 
            from_=1, 
            to=20, 
            textvariable=self.batch_size, 
            width=5
        ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 日志设置
        self.enable_logging = tk.BooleanVar(value=self.config.get("enable_logging", False))
        ttk.Checkbutton(
            self.advanced_frame, 
            text="启用API日志", 
            variable=self.enable_logging
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    def toggle_api_fields(self):
        """切换API设置界面"""
        api_type = self.api_type.get()
        if api_type == "DeepLX":
            self.deeplx_frame.grid()
            self.chatgpt_frame.grid_remove()
        else:  # ChatGPT
            self.deeplx_frame.grid_remove()
            self.chatgpt_frame.grid()
    
    def edit_system_prompt(self):
        """编辑系统提示词"""
        prompt_dialog = tk.Toplevel(self.dialog)
        prompt_dialog.title("编辑系统提示词")
        prompt_dialog.geometry("600x400")
        prompt_dialog.transient(self.dialog)
        prompt_dialog.grab_set()
        
        ttk.Label(prompt_dialog, text="输入系统提示词:").pack(anchor=tk.W, padx=10, pady=5)
        
        prompt_text = tk.Text(prompt_dialog, wrap=tk.WORD, height=15)
        prompt_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        prompt_text.insert(tk.END, self.system_prompt.get())
        
        button_frame = ttk.Frame(prompt_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_prompt():
            self.system_prompt.set(prompt_text.get(1.0, tk.END).strip())
            prompt_dialog.destroy()
        
        ttk.Button(button_frame, text="保存", command=save_prompt).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=prompt_dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def save_config(self):
        """保存配置"""
        config_data = {
            "api_type": self.api_type.get(),
            "deeplx_url": self.deeplx_url.get(),
            "chatgpt_base": self.chatgpt_base.get(),
            "chatgpt_key": self.chatgpt_key.get(),
            "chatgpt_model": self.chatgpt_model.get(),
            "system_prompt": self.system_prompt.get(),
            "batch_size": self.batch_size.get(),
            "enable_logging": self.enable_logging.get(),
            "target_lang": self.config.get("target_lang", "英语"),
            "last_file_type": self.config.get("last_file_type", "RESX")
        }
        
        self.result = config_data
        self.dialog.destroy()
    
    def cancel(self):
        """取消操作"""
        self.dialog.destroy()
    
    def show(self):
        """显示对话框并等待结果"""
        self.dialog.wait_window()
        return self.result 