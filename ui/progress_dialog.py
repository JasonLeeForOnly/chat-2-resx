import tkinter as tk
from tkinter import ttk

class ProgressDialog:
    def __init__(self, parent, translator=None):
        self.parent = parent
        self.translator = translator
        self.dialog = None
        self.setup_ui()
    
    def setup_ui(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("处理中")
        self.dialog.geometry("400x170")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # 进度信息
        self.status_label = ttk.Label(self.dialog, text="准备中...")
        self.status_label.pack(pady=(20, 5))
        
        self.progress_text = ttk.Label(self.dialog, text="0%")
        self.progress_text.pack(pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.dialog, 
            variable=self.progress_var, 
            maximum=100,
            length=350
        )
        self.progress_bar.pack(pady=5, padx=20)
        
        # 取消按钮
        self.cancel_button = ttk.Button(
            self.dialog, 
            text="取消", 
            command=self.on_cancel
        )
        self.cancel_button.pack(pady=10)
        
        # 阻止关闭按钮
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def update_progress(self, progress, current, total, status=None):
        """更新进度信息"""
        self.progress_var.set(progress)
        self.progress_text.config(text=f"{progress:.1f}% ({current}/{total})")
        
        if status:
            self.status_label.config(text=status)
        
        self.dialog.update()
    
    def set_cancel_callback(self, callback):
        """设置取消回调函数"""
        self.cancel_callback = callback
    
    def on_cancel(self):
        """取消操作"""
        # 调用取消翻译方法
        self.cancel_translation()
        
        # 如果有额外的回调，也调用它
        if hasattr(self, 'cancel_callback') and self.cancel_callback:
            self.cancel_callback()
    
    def close(self):
        """关闭对话框"""
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
    
    def cancel_translation(self):
        """取消翻译过程"""
        if self.translator and not isinstance(self.translator, str):
            try:
                # 直接调用翻译器的cancel方法
                self.translator.cancel()
                # 同时调用翻译服务的cancel方法
                if hasattr(self.translator, 'translation_service'):
                    self.translator.translation_service.cancel()
                    
                self.status_label.config(text="正在取消翻译...")
                self.cancel_button.config(state=tk.DISABLED)
            except Exception as e:
                import logging
                logging.error(f"取消翻译时出错: {str(e)}")
        else:
            # 如果translator不是有效对象，只更新UI
            self.status_label.config(text="正在取消翻译...")
            self.cancel_button.config(state=tk.DISABLED)
            
            # 记录错误信息
            import logging
            logging.error(f"无效的翻译器对象: {type(self.translator)}") 