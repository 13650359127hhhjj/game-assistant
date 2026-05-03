#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图形用户界面主窗口模块

负责实现应用程序的图形界面，包括：
- 错误诊断功能界面
- 资源搜索下载功能界面
- 结果展示区域
- 日志显示区域
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime

from core.error_detector import ErrorDetector
from core.resource_downloader import ResourceDownloader
from utils.logger import get_logger


class MainWindow:
    """主窗口类，负责构建和管理整个应用程序界面"""
    
    def __init__(self, root):
        """
        初始化主窗口
        
        Args:
            root: Tkinter根窗口对象
        """
        self.root = root
        self.logger = get_logger(__name__)
        self.error_detector = ErrorDetector()
        self.resource_downloader = ResourceDownloader()
        
        # 界面状态变量
        self.is_scanning = False
        self.is_downloading = False
        
        # 初始化界面
        self._setup_window()
        self._create_menu()
        self._create_widgets()
        self._bind_events()
        
        self.logger.info("主窗口初始化完成")
    
    def _setup_window(self):
        """配置主窗口属性"""
        self.root.title("智能游戏错误诊断与资源下载辅助系统 v1.0.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置窗口图标（如果有）
        # self.root.iconbitmap('icon.ico')
        
        # 设置窗口背景色
        self.root.configure(bg='#f0f0f0')
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出日志", command=self._export_log)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._quit_app)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建主容器
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建Notebook用于切换选项卡
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建错误诊断选项卡
        self.error_tab = self._create_error_tab()
        self.notebook.add(self.error_tab, text="错误诊断")
        
        # 创建资源下载选项卡
        self.resource_tab = self._create_resource_tab()
        self.notebook.add(self.resource_tab, text="资源下载")
        
        # 创建日志显示区域
        self._create_log_area(main_container)
        
        # 创建状态栏
        self._create_status_bar(main_container)
    
    def _create_error_tab(self):
        """创建错误诊断选项卡"""
        frame = ttk.Frame(self.notebook, padding="10")
        
        # 标题
        title_label = ttk.Label(
            frame, 
            text="游戏错误智能诊断",
            font=("微软雅黑", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 错误信息输入区域
        input_frame = ttk.LabelFrame(frame, text="请输入错误信息", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.error_input = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.error_input.pack(fill=tk.BOTH, expand=True)
        
        # 输入提示
        hint_label = ttk.Label(
            input_frame,
            text="提示：可以输入错误代码、错误描述或游戏截图描述",
            font=("微软雅黑", 9),
            foreground="gray"
        )
        hint_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.diagnose_btn = ttk.Button(
            button_frame,
            text="开始诊断",
            command=self._start_diagnose,
            width=15
        )
        self.diagnose_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="清空输入",
            command=lambda: self.error_input.delete(1.0, tk.END),
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # 诊断结果展示区域
        result_frame = ttk.LabelFrame(frame, text="诊断结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.diagnose_result = scrolledtext.ScrolledText(
            result_frame,
            height=10,
            font=("微软雅黑", 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.diagnose_result.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def _create_resource_tab(self):
        """创建资源下载选项卡"""
        frame = ttk.Frame(self.notebook, padding="10")
        
        # 标题
        title_label = ttk.Label(
            frame,
            text="游戏资源搜索下载",
            font=("微软雅黑", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 搜索区域
        search_frame = ttk.LabelFrame(frame, text="资源搜索", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X)
        
        ttk.Label(search_input_frame, text="关键词：").pack(side=tk.LEFT, padx=5)
        
        self.keyword_entry = ttk.Entry(search_input_frame, width=30)
        self.keyword_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.search_btn = ttk.Button(
            search_input_frame,
            text="搜索",
            command=self._start_search,
            width=10
        )
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # 资源类型选择
        type_frame = ttk.Frame(search_frame)
        type_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(type_frame, text="资源类型：").pack(side=tk.LEFT, padx=5)
        
        self.resource_type = tk.StringVar(value="all")
        type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.resource_type,
            values=["全部", "补丁", "MOD", "地图", "皮肤", "音效"],
            state="readonly",
            width=15
        )
        type_combo.pack(side=tk.LEFT, padx=5)
        
        # 搜索结果列表
        result_list_frame = ttk.LabelFrame(frame, text="搜索结果", padding="10")
        result_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建树形视图
        columns = ("编号", "资源名称", "类型", "大小", "来源")
        self.result_tree = ttk.Treeview(
            result_list_frame,
            columns=columns,
            show="headings",
            height=8
        )
        
        # 设置列标题
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=150, anchor=tk.W)
        
        # 添加滚动条
        vsb = ttk.Scrollbar(result_list_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=vsb.set)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 下载操作按钮
        download_btn_frame = ttk.Frame(frame)
        download_btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            download_btn_frame,
            text="下载选中",
            command=self._download_selected,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            download_btn_frame,
            text="清空列表",
            command=self._clear_result_list,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            download_btn_frame,
            text="刷新列表",
            command=self._refresh_results,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def _create_log_area(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="运行日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置标签用于不同颜色的日志
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("SUCCESS", foreground="green")
    
    def _create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.time_label = ttk.Label(
            status_frame,
            text="",
            relief=tk.SUNKEN,
            width=20
        )
        self.time_label.pack(side=tk.RIGHT)
        self._update_time()
    
    def _bind_events(self):
        """绑定事件处理"""
        # 绑定回车键搜索
        self.keyword_entry.bind("<Return>", lambda e: self._start_search())
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._quit_app)
    
    def _update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)
    
    def _add_log(self, message, level="INFO"):
        """
        添加日志消息到日志显示区域
        
        Args:
            message: 日志消息
            level: 日志级别 (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message, level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # 同时输出到日志器
        getattr(self.logger, level.lower())(message)
    
    def _start_diagnose(self):
        """开始错误诊断"""
        error_info = self.error_input.get(1.0, tk.END).strip()
        
        if not error_info:
            messagebox.showwarning("输入提示", "请先输入错误信息！")
            return
        
        if self.is_scanning:
            messagebox.showwarning("提示", "诊断正在进行中，请稍候...")
            return
        
        # 清空结果显示
        self.diagnose_result.config(state=tk.NORMAL)
        self.diagnose_result.delete(1.0, tk.END)
        self.diagnose_result.insert(1.0, "正在进行分析，请稍候...\n")
        self.diagnose_result.config(state=tk.DISABLED)
        
        # 更新状态
        self.is_scanning = True
        self.diagnose_btn.config(state=tk.DISABLED)
        self._update_status("正在诊断...")
        self._add_log("开始错误诊断分析", "INFO")
        
        # 在新线程中执行诊断
        thread = threading.Thread(target=self._diagnose_worker, args=(error_info,))
        thread.daemon = True
        thread.start()
    
    def _diagnose_worker(self, error_info):
        """
        后台诊断工作线程
        
        Args:
            error_info: 错误信息
        """
        try:
            result = self.error_detector.diagnose(error_info)
            
            # 在主线程中更新UI
            self.root.after(0, self._display_diagnose_result, result)
            
        except Exception as e:
            self.logger.error(f"诊断过程出错: {str(e)}")
            self.root.after(0, self._display_diagnose_error, str(e))
        
        finally:
            self.root.after(0, self._diagnose_complete)
    
    def _display_diagnose_result(self, result):
        """显示诊断结果"""
        self.diagnose_result.config(state=tk.NORMAL)
        self.diagnose_result.delete(1.0, tk.END)
        
        if result:
            output = "=" * 50 + "\n"
            output += "诊断结果\n"
            output += "=" * 50 + "\n\n"
            
            for i, item in enumerate(result, 1):
                output += f"【{i}】{item.get('title', '未知')}\n"
                output += f"    可能原因：{item.get('cause', '未知')}\n"
                output += f"    解决方案：{item.get('solution', '暂无')}\n"
                output += f"    置信度：{item.get('confidence', '0')}%\n"
                output += "-" * 50 + "\n"
        else:
            output = "未找到匹配的诊断结果，建议您提供更详细的错误信息。"
        
        self.diagnose_result.insert(1.0, output)
        self.diagnose_result.config(state=tk.DISABLED)
        
        self._add_log("诊断完成", "SUCCESS")
    
    def _display_diagnose_error(self, error_msg):
        """显示诊断错误"""
        self.diagnose_result.config(state=tk.NORMAL)
        self.diagnose_result.delete(1.0, tk.END)
        self.diagnose_result.insert(1.0, f"诊断过程出错：{error_msg}")
        self.diagnose_result.config(state=tk.DISABLED)
        
        self._add_log(f"诊断出错: {error_msg}", "ERROR")
    
    def _diagnose_complete(self):
        """诊断完成后的清理工作"""
        self.is_scanning = False
        self.diagnose_btn.config(state=tk.NORMAL)
        self._update_status("就绪")
    
    def _start_search(self):
        """开始资源搜索"""
        keyword = self.keyword_entry.get().strip()
        
        if not keyword:
            messagebox.showwarning("输入提示", "请输入搜索关键词！")
            return
        
        if self.is_downloading:
            messagebox.showwarning("提示", "当前有下载任务正在进行")
            return
        
        # 清空列表
        self._clear_result_list()
        
        # 更新状态
        self.is_downloading = True
        self.search_btn.config(state=tk.DISABLED)
        self._update_status("正在搜索...")
        self._add_log(f"开始搜索资源: {keyword}", "INFO")
        
        # 在新线程中执行搜索
        thread = threading.Thread(target=self._search_worker, args=(keyword,))
        thread.daemon = True
        thread.start()
    
    def _search_worker(self, keyword):
        """
        后台搜索工作线程
        
        Args:
            keyword: 搜索关键词
        """
        try:
            # 获取资源类型筛选
            resource_type = self.resource_type.get()
            type_filter = None if resource_type == "全部" else resource_type
            
            results = self.resource_downloader.search(keyword, resource_type=type_filter)
            
            # 在主线程中更新UI
            self.root.after(0, self._display_search_results, results)
            
        except Exception as e:
            self.logger.error(f"搜索过程出错: {str(e)}")
            self.root.after(0, self._display_search_error, str(e))
        
        finally:
            self.root.after(0, self._search_complete)
    
    def _display_search_results(self, results):
        """显示搜索结果"""
        # 清空现有结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        if not results:
            messagebox.showinfo("搜索结果", "未找到匹配的资源")
            return
        
        # 添加搜索结果
        for i, result in enumerate(results, 1):
            self.result_tree.insert("", tk.END, values=(
                i,
                result.get('name', '未知'),
                result.get('type', '未知'),
                result.get('size', '未知'),
                result.get('source', '未知')
            ))
        
        self._add_log(f"搜索完成，找到 {len(results)} 个结果", "SUCCESS")
    
    def _display_search_error(self, error_msg):
        """显示搜索错误"""
        messagebox.showerror("搜索错误", error_msg)
        self._add_log(f"搜索出错: {error_msg}", "ERROR")
    
    def _search_complete(self):
        """搜索完成后的清理工作"""
        self.is_downloading = False
        self.search_btn.config(state=tk.NORMAL)
        self._update_status("就绪")
    
    def _download_selected(self):
        """下载选中的资源"""
        selection = self.result_tree.selection()
        
        if not selection:
            messagebox.showwarning("选择提示", "请先选择要下载的资源！")
            return
        
        # 获取选中的项目
        item = self.result_tree.item(selection[0])
        values = item['values']
        
        resource_name = values[1]
        
        # 选择保存目录
        save_dir = filedialog.askdirectory(title="选择保存目录")
        
        if not save_dir:
            return
        
        self._add_log(f"开始下载: {resource_name}", "INFO")
        self._update_status("正在下载...")
        
        # 模拟下载过程（实际应用中这里会调用下载器）
        self.root.after(100, lambda: self._download_complete(resource_name))
    
    def _download_complete(self, resource_name):
        """下载完成"""
        self._update_status("就绪")
        self._add_log(f"下载完成: {resource_name}", "SUCCESS")
        messagebox.showinfo("下载完成", f"资源 [{resource_name}] 已下载完成！")
    
    def _clear_result_list(self):
        """清空搜索结果列表"""
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
    
    def _refresh_results(self):
        """刷新搜索结果"""
        keyword = self.keyword_entry.get().strip()
        if keyword:
            self._start_search()
        else:
            messagebox.showwarning("提示", "请先输入搜索关键词")
    
    def _update_status(self, status_text):
        """更新状态栏文本"""
        self.status_label.config(text=status_text)
    
    def _export_log(self):
        """导出日志到文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"game_assistant_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if not file_path:
            return
        
        try:
            log_content = self.log_text.get(1.0, tk.END)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            messagebox.showinfo("导出成功", f"日志已保存到：{file_path}")
            self._add_log(f"日志已导出到: {file_path}", "SUCCESS")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出日志时出错：{str(e)}")
            self._add_log(f"导出日志失败: {str(e)}", "ERROR")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
【智能游戏错误诊断与资源下载辅助系统】

使用说明：

1. 错误诊断功能：
   - 在错误信息输入框中输入游戏错误信息
   - 可以输入错误代码、错误描述或截图描述
   - 点击"开始诊断"按钮进行分析
   - 查看右侧的诊断结果和建议

2. 资源下载功能：
   - 输入搜索关键词
   - 选择资源类型筛选
   - 点击"搜索"按钮
   - 从结果列表中选择资源进行下载

3. 日志区域：
   - 显示系统运行日志
   - 可通过"文件->导出日志"保存日志

4. 其他功能：
   - 支持结果导出
   - 实时状态显示
   - 便捷的操作界面
        """
        messagebox.showinfo("使用帮助", help_text)
    
    def _show_about(self):
        """显示关于信息"""
        about_text = """
智能游戏错误诊断与资源下载辅助系统

版本：1.0.0

开发者：小米激励计划申请者

简介：
本系统旨在为游戏玩家提供便捷的错误诊断和
资源搜索下载服务，提升游戏体验。

技术栈：
- Python 3.x
- Tkinter (GUI)
- 多线程处理

© 2024 All Rights Reserved
        """
        messagebox.showinfo("关于", about_text)
    
    def _quit_app(self):
        """退出应用程序"""
        if messagebox.askokcancel("退出", "确定要退出应用程序吗？"):
            self._add_log("用户退出应用程序", "INFO")
            self.root.quit()
            self.root.destroy()
