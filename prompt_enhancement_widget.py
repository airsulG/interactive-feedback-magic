# Requirement Clarification Widget - 智能需求澄清组件
#
# === 核心创新功能 ===
# 本组件是项目的重要创新之一，提供智能需求澄清能力
#
# 🎯 功能价值:
# - 将用户的模糊想法转化为清晰的需求列表
# - 识别并澄清模糊概念和主观词汇
# - 明确功能边界、性能指标和验收标准
# - 专注于"做什么"而非"怎么做"，避免过早的方案设计
# - 实时流式显示，优化用户体验
#
# ⚡ 技术特性:
# - 集成 Google Gemini 2.5 Flash 模型
# - 支持上下文感知处理
# - 流式文本生成，实时反馈
# - 优雅的加载动画和状态提示
#
# 🎨 UI 设计:
# - shadcn/ui 风格的现代化界面
# - 直观的操作流程和状态反馈
# - 响应式布局和动画效果

from typing import Optional, Generator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QMovie

from ui_styles import Colors, Typography, Spacing, BorderRadius, ComponentStyles

class PromptEnhancementThread(QThread):
    """需求澄清处理线程"""

    # 信号定义
    chunk_received = Signal(str)  # 接收到文本块
    enhancement_finished = Signal()  # 澄清完成
    enhancement_failed = Signal(str)  # 澄清失败
    
    def __init__(self, original_text: str, context_info: str = ""):
        super().__init__()
        self.original_text = original_text
        self.context_info = context_info
    
    def run(self) -> None:
        """执行需求澄清"""
        try:
            # 动态导入，避免启动时的依赖问题
            from prompt_enhancer import enhance_prompt_with_gemini_stream_generator

            # 流式生成澄清文本
            for chunk in enhance_prompt_with_gemini_stream_generator(
                self.original_text,
                self.context_info
            ):
                if chunk.startswith("错误："):
                    self.enhancement_failed.emit(chunk)
                    return
                else:
                    self.chunk_received.emit(chunk)

            self.enhancement_finished.emit()

        except ImportError:
            self.enhancement_failed.emit(
                "错误：需求澄清功能不可用。请确保已安装 google-genai 依赖包。"
            )
        except Exception as e:
            self.enhancement_failed.emit(f"错误：需求澄清过程中发生异常：{str(e)}")

class PromptEnhancementWidget(QWidget):
    """
    智能需求澄清组件

    === 设计理念 ===
    这个组件体现了"AI 赋能人类创造力"的核心理念:
    - 降低表达门槛，让想法更容易传达
    - 澄清模糊概念，明确真实需求
    - 保持用户控制权，AI 只是助手
    """

    # 信号定义
    enhancement_completed = Signal(str)  # 澄清完成
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._enhancement_thread: Optional[PromptEnhancementThread] = None
        self._is_enhancing = False
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(int(Spacing.MD.replace('px', '')))
        
        # 标题区域
        self._create_title_section(layout)
        
        # 操作区域
        self._create_action_section(layout)
        
        # 状态区域
        self._create_status_section(layout)
    
    def _create_title_section(self, layout: QVBoxLayout) -> None:
        """创建标题区域"""
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 图标和标题
        title_label = QLabel("🔍 智能需求澄清")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_LG};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
            }}
        """)
        
        # 状态指示器
        self.status_indicator = QLabel("🤖")
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {Colors.ACCENT};
                font-size: {Typography.TEXT_LG};
                margin-left: {Spacing.SM};
            }}
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.status_indicator)
        title_layout.addStretch()
        
        layout.addWidget(title_container)
        
        # 描述文本
        desc_label = QLabel(
            "将你的模糊想法转化为清晰、具体的需求列表。"
            "AI 将识别模糊概念，明确功能边界和验收标准。"
        )
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_SM};
                line-height: {Typography.LEADING_RELAXED};
                margin-bottom: {Spacing.SM};
            }}
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
    
    def _create_action_section(self, layout: QVBoxLayout) -> None:
        """创建操作区域"""
        action_container = QWidget()
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(0, 0, 0, 0)
        
        # 澄清按钮
        self.enhance_button = QPushButton("🔍 开始澄清")
        self.enhance_button.setStyleSheet(ComponentStyles.button_accent())
        self.enhance_button.setToolTip(
            "使用 AI 智能分析和澄清你的需求\n"
            "• 识别模糊概念\n"
            "• 明确功能边界\n"
            "• 量化性能指标"
        )
        
        # 重置按钮
        self.reset_button = QPushButton("🔄 重置")
        self.reset_button.setStyleSheet(ComponentStyles.button_secondary())
        self.reset_button.setToolTip("恢复到澄清前的原始文本")
        self.reset_button.setEnabled(False)
        
        action_layout.addWidget(self.enhance_button)
        action_layout.addWidget(self.reset_button)
        action_layout.addStretch()
        
        layout.addWidget(action_container)
    
    def _create_status_section(self, layout: QVBoxLayout) -> None:
        """创建状态区域"""
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: {BorderRadius.SM};
                height: 6px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {Colors.ACCENT};
                border-radius: {BorderRadius.SM};
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # 状态文本
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_SM};
                margin-top: {Spacing.XS};
            }}
        """)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
    
    def _connect_signals(self) -> None:
        """连接信号"""
        self.enhance_button.clicked.connect(self._start_enhancement)
        self.reset_button.clicked.connect(self._reset_enhancement)
    
    def _start_enhancement(self) -> None:
        """开始需求澄清"""
        if self._is_enhancing:
            return

        # 获取文本编辑器（从父组件）
        text_edit = self._get_text_edit()
        if not text_edit:
            return

        original_text = text_edit.toPlainText().strip()
        if not original_text:
            self._show_status("请先输入一些文本内容", is_error=True)
            return

        # 保存原始文本
        self._original_text = original_text

        # 更新 UI 状态
        self._set_enhancing_state(True)

        # 启动澄清线程
        context_info = getattr(self.parent(), 'context_info', '')
        self._enhancement_thread = PromptEnhancementThread(original_text, context_info)
        self._enhancement_thread.chunk_received.connect(self._on_chunk_received)
        self._enhancement_thread.enhancement_finished.connect(self._on_enhancement_finished)
        self._enhancement_thread.enhancement_failed.connect(self._on_enhancement_failed)
        self._enhancement_thread.start()

        # 清空文本区域，准备流式显示
        text_edit.setPlainText("")
        self._enhanced_text = ""
    
    def _on_chunk_received(self, chunk: str) -> None:
        """处理接收到的文本块"""
        text_edit = self._get_text_edit()
        if text_edit:
            self._enhanced_text += chunk
            text_edit.setPlainText(self._enhanced_text)
            
            # 滚动到底部
            cursor = text_edit.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            text_edit.setTextCursor(cursor)
    
    def _on_enhancement_finished(self) -> None:
        """澄清完成处理"""
        self._set_enhancing_state(False)
        self._show_status("✅ 需求澄清完成！你可以继续编辑或直接使用。", is_success=True)
        self.reset_button.setEnabled(True)
        self.enhancement_completed.emit(self._enhanced_text)

    def _on_enhancement_failed(self, error_message: str) -> None:
        """澄清失败处理"""
        self._set_enhancing_state(False)
        self._show_status(error_message, is_error=True)

        # 恢复原始文本
        text_edit = self._get_text_edit()
        if text_edit and hasattr(self, '_original_text'):
            text_edit.setPlainText(self._original_text)

    def _reset_enhancement(self) -> None:
        """重置澄清"""
        if hasattr(self, '_original_text'):
            text_edit = self._get_text_edit()
            if text_edit:
                text_edit.setPlainText(self._original_text)
                self.reset_button.setEnabled(False)
                self._show_status("已恢复到原始文本", is_success=True)
    
    def _set_enhancing_state(self, is_enhancing: bool) -> None:
        """设置澄清状态"""
        self._is_enhancing = is_enhancing

        if is_enhancing:
            self.enhance_button.setText("⏳ 澄清中...")
            self.enhance_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条
            self.status_indicator.setText("🔄")
            self._show_status("正在使用 AI 分析和澄清你的需求...")
        else:
            self.enhance_button.setText("🔍 开始澄清")
            self.enhance_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.status_indicator.setText("🤖")
    
    def _show_status(self, message: str, is_error: bool = False, is_success: bool = False) -> None:
        """显示状态信息"""
        self.status_label.setText(message)
        self.status_label.setVisible(True)
        
        # 设置颜色
        if is_error:
            color = Colors.ERROR
        elif is_success:
            color = Colors.SUCCESS
        else:
            color = Colors.TEXT_SECONDARY
        
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_SM};
                margin-top: {Spacing.XS};
            }}
        """)
        
        # 自动隐藏状态（除了错误信息）
        if not is_error:
            QTimer.singleShot(3000, lambda: self.status_label.setVisible(False))
    
    def _get_text_edit(self) -> Optional[QTextEdit]:
        """获取文本编辑器组件"""
        # 从父组件中查找文本编辑器
        parent = self.parent()
        while parent:
            if hasattr(parent, 'feedback_text') and isinstance(parent.feedback_text, QTextEdit):
                return parent.feedback_text
            parent = parent.parent()
        return None
