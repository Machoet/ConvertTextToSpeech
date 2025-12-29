import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import asyncio
from datetime import datetime
import edge_tts

class TextToAudioConverterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文本转音频工具 v1.0")
        self.root.geometry("850x650")  # 稍微增加宽度以容纳语音选择
        self.root.resizable(True, True)
        
        # 设置图标和样式
        self.setup_style()
        
        # 日志文件设置
        self.log_file_path = self.get_dated_log_file()  # 按日期命名的日志文件
        self.init_log_file()  # 初始化日志文件
        
        # 语音配置
        self.setup_voice_config()
        
        # 创建主界面
        self.create_widgets()
        
        # 状态变量
        self.is_processing = False
        self.input_files = []  # 改为支持多个文件
        self.output_dir = ""
        
        # 语言到文件后缀的映射
        self.language_suffix_map = {
            "zh-CN": "Chinese",
            "en-US": "English",
            "ja-JP": "Japanese",
            "ko-KR": "Korean",
            "fr-FR": "French",
            "de-DE": "German",
            "es-ES": "Spanish",
            "ru-RU": "Russian"
        }
        
        # 日志文本
        self.log_content = ""
        
    def setup_style(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义颜色
        self.bg_color = "#f0f0f0"
        self.btn_color = "#4CAF50"
        self.text_bg = "#ffffff"
        
        self.root.configure(bg=self.bg_color)
    
    def setup_voice_config(self):
        """设置语音配置"""
        # 可用的语音列表 - Edge-TTS支持的神经语音
        self.voice_options = {
            # 中文语音
            "晓晓 (年轻女声-推荐)": "zh-CN-XiaoxiaoNeural",
            "云希 (年轻男声)": "zh-CN-YunxiNeural",
            "云扬 (新闻男声)": "zh-CN-YunyangNeural",
            "晓萱 (成熟女声)": "zh-CN-XiaoxuanNeural",
            "晓梦 (情感女声)": "zh-CN-XiaomengNeural",
            "晓颜 (聊天女声)": "zh-CN-XiaoruiNeural",
            
            # 英文语音
            "Jenny (美式英文-女)": "en-US-JennyNeural",
            "Guy (美式英文-男)": "en-US-GuyNeural",
            "Aria (美式英文-女)": "en-US-AriaNeural",
            "Davis (美式英文-男)": "en-US-DavisNeural",
            "Amber (美式英文-女)": "en-US-AmberNeural",
            "Ana (美式英文-女童)": "en-US-AnaNeural",
            
            # 日文语音
            "Nanami (日文-女)": "ja-JP-NanamiNeural",
            "Keita (日文-男)": "ja-JP-KeitaNeural",
            "Aoi (日文-女)": "ja-JP-AoiNeural",
            
            # 其他语言
            "法语-女声": "fr-FR-DeniseNeural",
            "德语-女声": "de-DE-KatjaNeural",
            "西班牙语-女声": "es-ES-ElviraNeural",
            "韩语-女声": "ko-KR-SunHiNeural",
            "俄语-女声": "ru-RU-SvetlanaNeural",
        }
        
        # 语音到语言的映射
        self.voice_to_language = {
            "zh-CN-XiaoxiaoNeural": "zh-CN",
            "zh-CN-YunxiNeural": "zh-CN",
            "zh-CN-YunyangNeural": "zh-CN",
            "zh-CN-XiaoxuanNeural": "zh-CN",
            "zh-CN-XiaomengNeural": "zh-CN",
            "zh-CN-XiaoruiNeural": "zh-CN",
            "en-US-JennyNeural": "en-US",
            "en-US-GuyNeural": "en-US",
            "en-US-AriaNeural": "en-US",
            "en-US-DavisNeural": "en-US",
            "en-US-AmberNeural": "en-US",
            "en-US-AnaNeural": "en-US",
            "ja-JP-NanamiNeural": "ja-JP",
            "ja-JP-KeitaNeural": "ja-JP",
            "ja-JP-AoiNeural": "ja-JP",
            "fr-FR-DeniseNeural": "fr-FR",
            "de-DE-KatjaNeural": "de-DE",
            "es-ES-ElviraNeural": "es-ES",
            "ko-KR-SunHiNeural": "ko-KR",
            "ru-RU-SvetlanaNeural": "ru-RU",
        }
        
        # 默认语音
        self.selected_voice = tk.StringVar(value="zh-CN-XiaoxiaoNeural")
    
    def get_dated_log_file(self):
        """获取按日期命名的日志文件路径"""
        date_str = datetime.now().strftime("%Y%m%d")
        log_dir = os.path.join(os.getcwd(), "logs")
        
        # 创建logs目录
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except Exception as e:
                print(f"创建日志目录失败: {e}")
                # 如果创建失败，使用当前目录
                log_dir = os.getcwd()
        
        return os.path.join(log_dir, f"log_{date_str}.txt")
    
    def init_log_file(self):
        """初始化日志文件"""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"文本转音频工具 (Edge-TTS版) - 日志文件\n")
                f.write(f"程序启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"日志文件: {self.log_file_path}\n")
                f.write(f"TTS引擎: Microsoft Edge-TTS\n")
                f.write("=" * 60 + "\n\n")
            print(f"日志文件已创建: {self.log_file_path}")
        except Exception as e:
            print(f"创建日志文件失败: {e}")
            # 如果写入失败，尝试使用备用路径
            self.log_file_path = os.path.join(os.getcwd(), "conversion_log.txt")
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(f"备用日志文件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                print(f"使用备用日志文件: {self.log_file_path}")
            except Exception as e2:
                print(f"创建备用日志文件失败: {e2}")
    
    def create_widgets(self):
        """创建界面组件"""
        
        # 标题
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(pady=15)
        
        tk.Label(title_frame, text="📝 文本转音频批量工具 (Edge-TTS版)", 
                font=("微软雅黑", 20, "bold"), 
                bg=self.bg_color, fg="#333333").pack()
        
        tk.Label(title_frame, text="支持多种高质量语音，批量转换文本文件为MP3音频文件", 
                font=("微软雅黑", 11), 
                bg=self.bg_color, fg="#666666").pack()
        
        # 文件选择区域
        file_frame = tk.LabelFrame(self.root, text=" 文件设置 ", 
                                  font=("微软雅黑", 11, "bold"),
                                  bg=self.bg_color, padx=20, pady=15)
        file_frame.pack(pady=10, padx=20, fill="x")
        
        # 输入文件选择（支持多选）
        input_frame = tk.Frame(file_frame, bg=self.bg_color)
        input_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(input_frame, text="输入文件:", 
                font=("微软雅黑", 10), 
                bg=self.bg_color, width=10, anchor="w").pack(side="left")
        
        # 创建列表框显示选中的文件
        self.file_list_frame = tk.Frame(input_frame, bg=self.text_bg, bd=1, relief="solid")
        self.file_list_frame.pack(side="left", padx=5, fill="x", expand=True)
        
        # 创建滚动条
        list_scrollbar = tk.Scrollbar(self.file_list_frame)
        list_scrollbar.pack(side="right", fill="y")
        
        # 创建文件列表框
        self.file_listbox = tk.Listbox(self.file_list_frame, 
                                      font=("微软雅黑", 9), 
                                      bg=self.text_bg, 
                                      fg="#333333",
                                      yscrollcommand=list_scrollbar.set,
                                      height=3,
                                      selectmode=tk.EXTENDED)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        list_scrollbar.config(command=self.file_listbox.yview)
        
        # 文件选择按钮
        button_subframe = tk.Frame(input_frame, bg=self.bg_color)
        button_subframe.pack(side="right")
        
        ttk.Button(button_subframe, text="多选文件...", 
                  command=self.browse_input_files,
                  width=10).pack(side="top", pady=2)
        
        ttk.Button(button_subframe, text="清除列表", 
                  command=self.clear_file_list,
                  width=10).pack(side="top", pady=2)
        
        # 输出目录设置
        output_frame = tk.Frame(file_frame, bg=self.bg_color)
        output_frame.pack(fill="x")
        
        tk.Label(output_frame, text="输出目录:", 
                font=("微软雅黑", 10), 
                bg=self.bg_color, width=10, anchor="w").pack(side="left")
        
        self.output_entry = tk.Entry(output_frame, font=("微软雅黑", 10), 
                                    width=40, bd=1, relief="solid")
        self.output_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        ttk.Button(output_frame, text="浏览...", 
                  command=self.browse_output_dir,
                  width=10).pack(side="right")
        
        # 文件命名规则提示
        naming_frame = tk.Frame(file_frame, bg=self.bg_color)
        naming_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(naming_frame, text="输出命名规则:", 
                font=("微软雅黑", 9), 
                bg=self.bg_color, fg="#666666").pack(side="left")
        
        # 在 create_widgets 方法中找到命名规则标签部分
        self.naming_rule_label = tk.Label(naming_frame, 
                                 text="[原文件名]_[英文语音名].mp3",  # 修改这里
                                 font=("微软雅黑", 9, "italic"), 
                                 bg=self.bg_color, fg="#4CAF50")
        
        self.naming_rule_label.pack(side="left", padx=10)
        
        # 语音设置区域
        voice_frame = tk.LabelFrame(self.root, text=" 语音设置 ", 
                                   font=("微软雅黑", 11, "bold"),
                                   bg=self.bg_color, padx=20, pady=15)
        voice_frame.pack(pady=10, padx=20, fill="x")
        
        # 语音选择
        voice_select_frame = tk.Frame(voice_frame, bg=self.bg_color)
        voice_select_frame.pack(fill="x", pady=5)
        
        tk.Label(voice_select_frame, text="选择语音:", 
                font=("微软雅黑", 10), 
                bg=self.bg_color, width=10, anchor="w").pack(side="left")
        
        # 创建语音选择下拉框
        self.voice_combobox = ttk.Combobox(voice_select_frame, 
                                          textvariable=self.selected_voice,
                                          font=("微软雅黑", 10),
                                          width=40,
                                          state="readonly")
        self.voice_combobox.pack(side="left", padx=5, fill="x", expand=True)
        
        # 设置下拉框选项
        voice_display_names = list(self.voice_options.keys())
        self.voice_combobox['values'] = voice_display_names
        
        # 设置默认值
        self.voice_combobox.set("晓晓 (年轻女声-推荐)")
        
        # 语速设置
        speed_frame = tk.Frame(voice_frame, bg=self.bg_color)
        speed_frame.pack(fill="x", pady=5)
        
        tk.Label(speed_frame, text="语速:", 
                font=("微软雅黑", 10), 
                bg=self.bg_color, width=10, anchor="w").pack(side="left")
        
        self.speed_var = tk.StringVar(value="+0%")
        speeds = [("较慢", "-20%"), ("稍慢", "-10%"), ("正常", "+0%"), ("稍快", "+10%"), ("较快", "+20%")]
        
        for text, value in speeds:
            tk.Radiobutton(speed_frame, text=text, variable=self.speed_var, 
                          value=value, bg=self.bg_color, 
                          font=("微软雅黑", 9)).pack(side="left", padx=10)
        
        # 音量设置
        volume_frame = tk.Frame(voice_frame, bg=self.bg_color)
        volume_frame.pack(fill="x", pady=5)
        
        tk.Label(volume_frame, text="音量:", 
                font=("微软雅黑", 10), 
                bg=self.bg_color, width=10, anchor="w").pack(side="left")
        
        self.volume_var = tk.StringVar(value="+0%")
        volumes = [("较低", "-20%"), ("稍低", "-10%"), ("正常", "+0%"), ("稍高", "+10%"), ("较高", "+20%")]
        
        for text, value in volumes:
            tk.Radiobutton(volume_frame, text=text, variable=self.volume_var, 
                          value=value, bg=self.bg_color, 
                          font=("微软雅黑", 9)).pack(side="left", padx=10)
        
        # 控制按钮区域
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        self.convert_btn = ttk.Button(button_frame, text="开始批量转换", 
                                     command=self.start_conversion,
                                     width=15, style="Accent.TButton")
        self.convert_btn.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="清除日志", 
                  command=self.clear_log,
                  width=15).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="查看日志文件", 
                  command=self.open_log_file,
                  width=15).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="测试语音", 
                  command=self.test_voice,
                  width=15).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="退出程序", 
                  command=self.root.quit,
                  width=15).pack(side="left", padx=5)
        
        # 进度显示
        self.progress_frame = tk.Frame(self.root, bg=self.bg_color)
        self.progress_frame.pack(pady=(0, 10), padx=20, fill="x")
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                           variable=self.progress_var,
                                           maximum=100, length=780)
        self.progress_bar.pack()
        
        # 进度信息标签
        self.progress_info = tk.Label(self.root, text="等待转换...", 
                                     font=("微软雅黑", 9), 
                                     bg=self.bg_color, fg="#666666")
        self.progress_info.pack()
        
        self.status_label = tk.Label(self.root, text="就绪", 
                                    font=("微软雅黑", 10), 
                                    bg=self.bg_color, fg="#666666")
        self.status_label.pack()
        
        # 日志显示区域
        log_frame = tk.LabelFrame(self.root, text=" 日志输出 ", 
                                 font=("微软雅黑", 11, "bold"),
                                 bg=self.bg_color, padx=10, pady=10)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 日志文件路径提示
        log_info_frame = tk.Frame(log_frame, bg=self.bg_color)
        log_info_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        log_path_text = f"日志文件: {os.path.basename(self.log_file_path)}"
        if len(log_path_text) > 50:
            log_path_text = f"日志文件: ...{os.path.basename(self.log_file_path)[-40:]}"
        
        tk.Label(log_info_frame, text=log_path_text,
                font=("微软雅黑", 8),
                bg=self.bg_color, fg="#666666").pack(side="left")
        
        tk.Label(log_info_frame, text=f"位置: {os.path.dirname(self.log_file_path)}",
                font=("微软雅黑", 8),
                bg=self.bg_color, fg="#666666").pack(side="right")
        
        # 创建文本滚动区域
        log_container = tk.Frame(log_frame, bg=self.text_bg)
        log_container.pack(fill="both", expand=True)
        
        # 创建滚动条
        scrollbar = tk.Scrollbar(log_container)
        scrollbar.pack(side="right", fill="y")
        
        # 创建日志文本框
        self.log_text = tk.Text(log_container, font=("Consolas", 9), 
                               bg=self.text_bg, fg="#333333",
                               yscrollcommand=scrollbar.set,
                               wrap="word", height=10)
        self.log_text.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=self.log_text.yview)
        
        # 默认输出路径
        default_output_dir = os.path.join(os.getcwd(), "audio_output")
        self.output_entry.insert(0, default_output_dir)
        
        # 设置样式
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#4CAF50")
        
    def get_output_filename(self, input_file):
        """根据规则生成输出文件名"""
        # 获取原文件名（不含扩展名）
        base_name = os.path.splitext(os.path.basename(input_file))[0]
    
        # 获取选中的语音ID
        voice_display_name = self.voice_combobox.get()
        voice_id = self.voice_options.get(voice_display_name, "")
    
        # 语音后缀映射表
        voice_suffix_map = {
            "zh-CN-XiaoxiaoNeural": "Xiaoxiao",
            "zh-CN-YunxiNeural": "Yunxi",
            "zh-CN-YunyangNeural": "Yunyang",
            "zh-CN-XiaoxuanNeural": "Xiaoxuan",
            "zh-CN-XiaomengNeural": "Xiaomeng",
            "zh-CN-XiaoruiNeural": "Xiaorui",
            "en-US-JennyNeural": "Jenny",
            "en-US-GuyNeural": "Guy",
            "en-US-AriaNeural": "Aria",
            "en-US-DavisNeural": "Davis",
            "en-US-AmberNeural": "Amber",
            "en-US-AnaNeural": "Ana",
            "ja-JP-NanamiNeural": "Nanami",
            "ja-JP-KeitaNeural": "Keita",
            "ja-JP-AoiNeural": "Aoi",
            "fr-FR-DeniseNeural": "Denise",
            "de-DE-KatjaNeural": "Katja",
            "es-ES-ElviraNeural": "Elvira",
            "ko-KR-SunHiNeural": "SunHi",
            "ru-RU-SvetlanaNeural": "Svetlana",
        }
    
        # 获取英文后缀
        if voice_id in voice_suffix_map:
            voice_suffix = voice_suffix_map[voice_id]
        else:
            # 如果不在映射表中，尝试从ID提取
            if voice_id and "-" in voice_id:
                parts = voice_id.split("-")
                if len(parts) >= 3:
                    name = parts[-1]
                    # 去掉"Neural"后缀
                    if name.endswith("Neural"):
                        voice_suffix = name[:-6]
                    else:
                        voice_suffix = name
                else:
                    voice_suffix = voice_id
            else:
                voice_suffix = "Unknown"
    
        # 生成文件名
        filename = f"{base_name}_{voice_suffix}.mp3"
    
        return filename
    
    def browse_input_files(self):
        """浏览多个输入文件"""
        file_paths = filedialog.askopenfilenames(
            title="选择文本文件（可多选）",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_paths:
            # 清空列表
            self.file_listbox.delete(0, tk.END)
            self.input_files = []
            
            # 添加新文件
            for file_path in file_paths:
                self.input_files.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
            
            # 更新列表框高度
            file_count = len(self.input_files)
            self.file_listbox.config(height=min(5, max(3, file_count)))
            
            self.log(f"选择了 {file_count} 个文件")
            
            # 自动生成输出目录
            if file_count == 1:
                # 单个文件，使用其所在目录
                base_dir = os.path.dirname(self.input_files[0])
                default_output = os.path.join(base_dir, "audio_output")
            else:
                # 多个文件，使用第一个文件所在目录的父目录
                first_file_dir = os.path.dirname(self.input_files[0])
                default_output = os.path.join(os.path.dirname(first_file_dir), "audio_output")
            
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, default_output)
            
    def clear_file_list(self):
        """清除文件列表"""
        if self.input_files:
            if messagebox.askyesno("确认", f"确定要清除已选的 {len(self.input_files)} 个文件吗？"):
                self.file_listbox.delete(0, tk.END)
                self.input_files = []
                self.file_listbox.config(height=3)
                self.log("已清除文件列表")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(
            title="选择输出目录"
        )
        
        if dir_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dir_path)
            self.output_dir = dir_path
            self.log(f"设置输出目录: {dir_path}")
    
    def log(self, message, level="INFO"):
        """添加日志消息并保存到文件"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 确定日志级别
        if level == "ERROR":
            color = "#ff4444"
            prefix = "[错误]"
        elif level == "WARNING":
            color = "#ffaa00"
            prefix = "[警告]"
        elif level == "SUCCESS":
            color = "#44aa44"
            prefix = "[成功]"
        else:
            color = "#333333"
            prefix = "[信息]"
        
        # 文件日志消息
        file_log_message = f"{timestamp} {prefix} {message}"
        
        # GUI显示消息
        gui_log_message = f"{timestamp} {prefix} {message}\n"
        
        # 1. 写入日志文件
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(file_log_message + "\n")
        except Exception as e:
            # 如果写入失败，尝试在控制台输出
            print(f"写入日志文件失败: {e}")
            print(f"原日志内容: {file_log_message}")
        
        # 2. 显示在GUI文本框
        self.log_text.insert(tk.END, gui_log_message)
        
        # 为不同级别的日志设置颜色
        start_index = self.log_text.search(prefix, "end-2l linestart", stopindex="end")
        if start_index:
            end_index = f"{start_index}+{len(prefix)}c"
            self.log_text.tag_add(level, start_index, end_index)
            self.log_text.tag_config(level, foreground=color)
        
        # 滚动到底部
        self.log_text.see(tk.END)
        
        # 更新状态标签
        if level != "INFO":
            self.status_label.config(text=message)
        
        # 强制刷新界面
        self.root.update_idletasks()
    
    def clear_log(self):
        """清除日志"""
        # 询问确认
        if not messagebox.askyesno("确认", "确定要清除所有日志吗？\n（这将清空界面显示，但不会删除日志文件）"):
            return
        
        # 清空GUI显示
        self.log_text.delete(1.0, tk.END)
        self.log("日志显示已清除")
    
    def open_log_file(self):
        """打开日志文件"""
        if os.path.exists(self.log_file_path):
            try:
                if sys.platform == "win32":
                    os.startfile(self.log_file_path)
                elif sys.platform == "darwin":
                    os.system(f'open "{self.log_file_path}"')
                else:
                    os.system(f'xdg-open "{self.log_file_path}"')
                self.log(f"已打开日志文件: {os.path.basename(self.log_file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开日志文件:\n{str(e)}")
                self.log(f"打开日志文件失败: {str(e)}", "ERROR")
        else:
            messagebox.showinfo("提示", "日志文件不存在，可能是首次运行或日志文件被删除。")
            self.log("日志文件不存在", "WARNING")
    
    def test_voice(self):
        """测试当前选择的语音"""
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，请稍候...")
            return
        
        voice_display_name = self.voice_combobox.get()
        voice_id = self.voice_options.get(voice_display_name)
        
        if not voice_id:
            messagebox.showerror("错误", "请先选择一个有效的语音！")
            return
        
        # 创建测试文本
        test_text = ""
        if "zh-CN" in voice_id:
            test_text = "这是一段测试语音，用于检查当前选择的语音效果。"
        elif "en-US" in voice_id:
            test_text = "This is a test voice to check the effect of the selected voice."
        elif "ja-JP" in voice_id:
            test_text = "これはテスト音声です、選択した音声の効果を確認するために。"
        else:
            test_text = "This is a test voice."
        
        self.log(f"开始测试语音: {voice_display_name}")
        
        # 在新线程中运行测试
        threading.Thread(target=self.run_voice_test, args=(voice_id, test_text), daemon=True).start()
    
    async def async_test_voice(self, voice_id, test_text):
        """异步测试语音"""
        try:
            # 创建临时文件
            temp_file = os.path.join(os.getcwd(), "voice_test_temp.mp3")
            
            # 使用Edge-TTS生成语音
            communicate = edge_tts.Communicate(
                test_text,
                voice=voice_id,
                rate=self.speed_var.get(),
                volume=self.volume_var.get()
            )
            
            await communicate.save(temp_file)
            
            # 播放音频文件
            if os.path.exists(temp_file):
                # 根据操作系统播放音频
                if sys.platform == "win32":
                    os.startfile(temp_file)
                elif sys.platform == "darwin":
                    os.system(f'open "{temp_file}"')
                else:
                    os.system(f'xdg-open "{temp_file}"')
                
                self.log(f"语音测试完成，正在播放: {voice_id}")
                
                # 5秒后删除临时文件
                self.root.after(5000, lambda: self.cleanup_test_file(temp_file))
            else:
                self.log("测试文件生成失败", "ERROR")
                
        except Exception as e:
            self.log(f"语音测试失败: {str(e)}", "ERROR")
    
    def run_voice_test(self, voice_id, test_text):
        """运行语音测试"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.async_test_voice(voice_id, test_text))
            loop.close()
        except Exception as e:
            self.log(f"语音测试运行时错误: {str(e)}", "ERROR")
    
    def cleanup_test_file(self, temp_file):
        """清理测试文件"""
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
    
    def start_conversion(self):
        """开始批量转换"""
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，请稍候...")
            return
            
        # 检查是否有输入文件
        if not self.input_files:
            messagebox.showerror("错误", "请选择至少一个输入文件！")
            return
        
        # 获取输出目录
        self.output_dir = self.output_entry.get().strip()
        if not self.output_dir:
            messagebox.showerror("错误", "请设置输出目录！")
            return
        
        # 检查输出目录是否存在，不存在则创建
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
                self.log(f"创建输出目录: {self.output_dir}")
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出目录：\n{str(e)}")
                return
        
        # 开始转换线程
        self.is_processing = True
        self.convert_btn.config(state="disabled")
        self.progress_var.set(0)
        
        threading.Thread(target=self.convert_thread, daemon=True).start()
    
    def convert_thread(self):
        """批量转换线程"""
        try:
            total_files = len(self.input_files)
            voice_display_name = self.voice_combobox.get()
            voice_id = self.voice_options.get(voice_display_name)
            
            self.log("=" * 60)
            self.log(f"开始批量转换，共 {total_files} 个文件")
            self.log(f"输出目录: {self.output_dir}")
            self.log(f"选择语音: {voice_display_name}")
            self.log(f"语音ID: {voice_id}")
            self.log(f"语速: {self.speed_var.get()}")
            self.log(f"音量: {self.volume_var.get()}")
            
            success_count = 0
            fail_count = 0
            
            for i, input_file in enumerate(self.input_files):
                if not self.is_processing:  # 用户可能中途取消
                    break
                    
                self.log(f"正在处理文件 {i+1}/{total_files}: {os.path.basename(input_file)}")
                self.update_progress_info(f"正在处理文件 {i+1}/{total_files}: {os.path.basename(input_file)}")
                
                # 更新总体进度
                progress = (i / total_files) * 100
                self.update_progress(progress, f"处理文件 {i+1}/{total_files}")
                
                # 处理单个文件
                success = self.convert_single_file(input_file, voice_id)
                
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                
                # 短暂暂停，避免请求过快
                time.sleep(0.5)
            
            # 完成所有文件
            self.update_progress(100, "批量转换完成")
            
            self.log("=" * 60)
            self.log(f"🎉 批量转换完成！", "SUCCESS")
            self.log(f"📊 统计: 成功 {success_count} 个，失败 {fail_count} 个")
            self.log(f"📁 输出目录: {self.output_dir}")
            self.log(f"🎙️ 使用语音: {voice_display_name}")
            self.log(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.log("=" * 60)
            
            # 记录转换摘要
            self.log_batch_summary(total_files, success_count, fail_count, voice_display_name)
            
            # 询问是否打开输出目录
            self.root.after(100, lambda: self.ask_open_output_dir(success_count, fail_count))
            
            self.finish_conversion(True)
            
        except Exception as e:
            self.log(f"批量转换过程中发生错误: {str(e)}", "ERROR")
            self.finish_conversion(False)
    
    async def async_convert_file(self, text_content, output_file, voice_id):
        """异步转换单个文件"""
        try:
            communicate = edge_tts.Communicate(
                text_content,
                voice=voice_id,
                rate=self.speed_var.get(),
                volume=self.volume_var.get()
            )
            
            await communicate.save(output_file)
            return True
        except Exception as e:
            self.log(f"Edge-TTS转换失败: {str(e)}", "ERROR")
            return False
    
    def convert_single_file(self, input_file, voice_id):
        """转换单个文件"""
        try:
            self.log(f"--- 开始转换文件: {os.path.basename(input_file)} ---")
            
            # 检查文件是否存在
            if not os.path.exists(input_file):
                self.log(f"文件不存在: {input_file}", "ERROR")
                return False
            
            # 步骤1：读取文件
            text_content = self.read_text_file(input_file)
            
            if text_content is None:
                self.log(f"读取文件失败: {input_file}", "ERROR")
                return False
            
            text_length = len(text_content)
            self.log(f"读取成功，文本长度: {text_length} 字符")
            
            # 检查文本长度（Edge-TTS支持较长文本，但建议分段处理）
            if text_length > 10000:
                self.log(f"文本较长 ({text_length} 字符)，建议分割处理", "WARNING")
                # 这里可以添加文本分割逻辑
            
            # 步骤2：生成输出文件名
            output_filename = self.get_output_filename(input_file)
            output_file = os.path.join(self.output_dir, output_filename)
            
            # 避免文件名重复（如果重名才添加序号）
            counter = 1
            original_output_file = output_file
            base_name_without_ext = os.path.splitext(output_filename)[0]
            
            while os.path.exists(output_file):
                # 如果文件已存在，添加序号
                new_filename = f"{base_name_without_ext}_{counter:03d}.mp3"
                output_file = os.path.join(self.output_dir, new_filename)
                counter += 1
                if counter > 100:  # 避免无限循环
                    break
            
            if output_file != original_output_file:
                self.log(f"文件名重复，添加序号: {os.path.basename(output_file)}", "WARNING")
            
            # 步骤3：使用Edge-TTS转换为音频
            self.log(f"正在使用Edge-TTS生成音频...")
            
            # 创建异步事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 异步执行转换
                success = loop.run_until_complete(
                    self.async_convert_file(text_content, output_file, voice_id)
                )
            finally:
                loop.close()
            
            if not success:
                return False
            
            # 检查最终文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                file_size_mb = file_size / (1024 * 1024)
                
                self.log(f"✅ 文件转换成功: {os.path.basename(output_file)} ({file_size_mb:.2f} MB)", "SUCCESS")
                self.log(f"--- 完成转换文件: {os.path.basename(input_file)} ---")
                return True
            else:
                self.log("音频文件生成失败", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"转换文件时出错: {str(e)}", "ERROR")
            return False
    
    def log_batch_summary(self, total_files, success_count, fail_count, voice_name):
        """记录批量转换摘要到日志文件"""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write("\n" + "=" * 70 + "\n")
                f.write("批量转换摘要\n")
                f.write("=" * 70 + "\n")
                f.write(f"转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总文件数: {total_files}\n")
                f.write(f"成功: {success_count}\n")
                f.write(f"失败: {fail_count}\n")
                f.write(f"输出目录: {self.output_dir}\n")
                f.write(f"使用语音: {voice_name}\n")
                f.write(f"语速设置: {self.speed_var.get()}\n")
                f.write(f"音量设置: {self.volume_var.get()}\n")
                f.write("=" * 70 + "\n\n")
        except Exception as e:
            print(f"记录批量转换摘要失败: {e}")
    
    def read_text_file(self, file_path):
        """读取文本文件"""
        try:
            # 尝试不同编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except (UnicodeDecodeError, LookupError):
                    continue
            
            # 如果都失败，使用二进制读取
            with open(file_path, 'rb') as f:
                content = f.read()
                return content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            self.log(f"读取文件失败: {str(e)}", "ERROR")
            return None
    
    def split_long_text(self, text, max_length=10000):
        """分割长文本（Edge-TTS支持较长文本，这里保持原逻辑）"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # 按句子分割（中文标点）
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in ['。', '！', '？', '.', '!', '?', '\n']:
                sentences.append(current_sentence)
                current_sentence = ""
        
        if current_sentence:
            sentences.append(current_sentence)
        
        # 合并句子成合适的块
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def update_progress(self, value, message):
        """更新进度"""
        self.progress_var.set(value)
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_progress_info(self, message):
        """更新进度信息"""
        self.progress_info.config(text=message)
        self.root.update_idletasks()
    
    def finish_conversion(self, success):
        """完成转换"""
        self.is_processing = False
        
        if success:
            self.progress_var.set(100)
            self.status_label.config(text="批量转换完成！", fg="#44aa44")
            self.progress_info.config(text="批量转换完成！")
        else:
            self.status_label.config(text="转换失败", fg="#ff4444")
            self.progress_info.config(text="转换失败")
        
        self.convert_btn.config(state="normal")
    
    def ask_open_output_dir(self, success_count, fail_count):
        """询问是否打开输出目录"""
        message = f"批量转换完成！\n成功: {success_count} 个，失败: {fail_count} 个\n\n是否打开输出目录？"
        result = messagebox.askyesno("转换完成", message)
        if result:
            self.open_output_dir()
    
    def open_output_dir(self):
        """打开输出目录"""
        try:
            if os.path.exists(self.output_dir):
                if sys.platform == "win32":
                    os.startfile(self.output_dir)
                elif sys.platform == "darwin":
                    os.system(f'open "{self.output_dir}"')
                else:
                    os.system(f'xdg-open "{self.output_dir}"')
            else:
                self.log(f"输出目录不存在: {self.output_dir}", "WARNING")
        except Exception as e:
            self.log(f"无法打开目录: {str(e)}", "WARNING")
    
    def run(self):
        """运行程序"""
        self.log(f"程序启动 - 文本转音频批量工具 (Edge-TTS版) v1.0")
        self.log(f"日志文件位置: {self.log_file_path}")
        self.log(f"当前工作目录: {os.getcwd()}")
        self.log(f"可用语音数量: {len(self.voice_options)} 种")
        self.log("=" * 50)
        self.log("欢迎使用文本转音频批量工具")
        self.log("支持多种高质量语音，请选择语音和文件开始转换")
        self.log("点击'测试语音'按钮可以预览当前选择的语音效果")
        self.log("=" * 50)
        self.root.mainloop()

# 安装检查函数
def check_dependencies():
    """检查依赖包"""
    required_packages = ['edge-tts']
    
    print("正在检查依赖包...")
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            
            # 询问是否安装
            response = input(f"是否要安装 {package}？(y/n): ")
            if response.lower() == 'y':
                try:
                    import subprocess
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"✓ {package} 安装成功")
                except Exception as e:
                    print(f"安装 {package} 失败: {e}")
                    return False
            else:
                return False
    
    print("\n" + "="*50)
    print("依赖检查完成！")
    print("="*50 + "\n")
    return True

def main():
    """主函数"""
    print("="*50)
    print("文本转音频批量工具 - Edge-TTS版")
    print("="*50)
    print("\n功能特点:")
    print("1. 📁 支持多文件批量转换")
    print("2. 🎙️ 使用微软Edge-TTS高质量神经语音")
    print("3. 🌐 支持多种语言和语音（21种高质量语音）")
    print("4. 🔊 可调节语速和音量")
    print("5. 🎧 支持语音测试预览")
    print("6. 📊 实时显示转换进度")
    print("7. 📝 详细的日志记录（自动保存到文件）")
    print("8. 📦 自动命名：原文件名_语音名.mp3")
    print("\n注意: Edge-TTS需要网络连接才能工作")
    print("="*50 + "\n")
    
    # 检查依赖
    if not check_dependencies():
        print("请先安装必要的依赖包！")
        print("运行命令: pip install edge-tts")
        input("按回车键退出...")
        return
    
    # 运行图形界面
    app = TextToAudioConverterGUI()
    app.run()

if __name__ == "__main__":
    main()