import tkinter as tk
from tkinter import ttk

class ProgressDialog:
    def __init__(self, parent, title="处理中"):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x170")
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
        self.cancel_callback = None
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
        if self.cancel_callback:
            self.cancel_callback()
    
    def close(self):
        """关闭对话框"""
        self.dialog.grab_release()
        self.dialog.destroy() 