# Session Control Component - 会话控制组件
#
# === 核心创新功能 ===
# 本模块实现了智能会话控制机制，这是项目的重要改进之一
#
# 🎯 功能价值:
# - 让用户完全掌控与 AI 的交互流程
# - 避免不必要的 API 调用，节省成本
# - 提供清晰的会话状态反馈
# - 支持灵活的交互模式切换
#
# 🔄 会话状态:
# - CONTINUE: 继续当前会话，AI 将等待进一步指令
# - TERMINATE: 终止当前会话，AI 完成当前任务后结束
# - PAUSE: 暂停会话，用户可稍后继续
#
# 🎨 UI 设计:
# - 现代化的 shadcn/ui 风格
# - 直观的图标和文字说明
# - 清晰的状态指示
# - 响应式交互反馈

from enum import Enum
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QRadioButton, QButtonGroup, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui_styles import Colors, Typography, Spacing, BorderRadius, ComponentStyles

class SessionState(Enum):
    """会话状态枚举"""
    CONTINUE = "continue"
    TERMINATE = "terminate"
    PAUSE = "pause"

class SessionControlWidget(QWidget):
    """
    会话控制组件
    
    === 设计理念 ===
    这个组件体现了本项目"用户为中心"的设计理念:
    - 用户始终掌控交互流程
    - 清晰的状态反馈和选项说明
    - 优雅的视觉设计和交互体验
    """
    
    # 信号定义
    state_changed = Signal(str)  # 会话状态改变信号
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_state = SessionState.CONTINUE
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(int(Spacing.MD.replace('px', '')))
        
        # 标题区域
        self._create_title_section(layout)
        
        # 选项区域
        self._create_options_section(layout)
        
        # 说明区域
        self._create_description_section(layout)
    
    def _create_title_section(self, layout: QVBoxLayout) -> None:
        """创建标题区域"""
        title_label = QLabel("🔄 会话控制")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_LG};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                margin-bottom: {Spacing.SM};
            }}
        """)
        layout.addWidget(title_label)
        
        # 分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"""
            QFrame {{
                color: {Colors.BORDER};
                background-color: {Colors.BORDER};
                border: none;
                height: 1px;
                margin: {Spacing.SM} 0;
            }}
        """)
        layout.addWidget(separator)
    
    def _create_options_section(self, layout: QVBoxLayout) -> None:
        """创建选项区域"""
        self.button_group = QButtonGroup(self)
        
        # 继续会话选项
        self.continue_radio = self._create_radio_button(
            "🚀 继续会话",
            "AI 将等待你的进一步指令，保持当前对话上下文",
            SessionState.CONTINUE,
            checked=True
        )
        
        # 终止会话选项
        self.terminate_radio = self._create_radio_button(
            "✅ 完成任务",
            "AI 将完成当前任务并结束会话，不再等待反馈",
            SessionState.TERMINATE
        )
        
        # 暂停会话选项（未来功能）
        self.pause_radio = self._create_radio_button(
            "⏸️ 暂停会话",
            "暂停当前会话，稍后可以继续（开发中）",
            SessionState.PAUSE,
            enabled=False
        )
        
        # 添加到布局
        for radio in [self.continue_radio, self.terminate_radio, self.pause_radio]:
            layout.addWidget(radio)
    
    def _create_radio_button(
        self, 
        title: str, 
        description: str, 
        state: SessionState,
        checked: bool = False,
        enabled: bool = True
    ) -> QWidget:
        """创建单选按钮组件"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(
            int(Spacing.MD.replace('px', '')), 
            int(Spacing.SM.replace('px', '')),
            int(Spacing.MD.replace('px', '')), 
            int(Spacing.SM.replace('px', ''))
        )
        container_layout.setSpacing(int(Spacing.XS.replace('px', '')))
        
        # 主选项
        radio = QRadioButton(title)
        radio.setChecked(checked)
        radio.setEnabled(enabled)
        radio.setProperty("session_state", state.value)
        
        # 应用样式
        radio.setStyleSheet(ComponentStyles.radio_button())
        
        # 描述文本
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY if enabled else Colors.TEXT_DISABLED};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_SM};
                margin-left: 24px;
                line-height: {Typography.LEADING_RELAXED};
            }}
        """)
        desc_label.setWordWrap(True)
        
        container_layout.addWidget(radio)
        container_layout.addWidget(desc_label)
        
        # 添加到按钮组
        self.button_group.addButton(radio)
        
        # 容器样式
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.SURFACE if enabled else Colors.BACKGROUND};
                border: 1px solid {Colors.BORDER};
                border-radius: {BorderRadius.MD};
                margin: {Spacing.XS} 0;
            }}
            QWidget:hover {{
                background-color: {Colors.SURFACE_HOVER if enabled else Colors.BACKGROUND};
                border-color: {Colors.BORDER_HOVER if enabled else Colors.BORDER};
            }}
        """)
        
        return container
    
    def _create_description_section(self, layout: QVBoxLayout) -> None:
        """创建说明区域"""
        info_container = QFrame()
        info_container.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: {BorderRadius.MD};
                padding: {Spacing.MD};
                margin-top: {Spacing.SM};
            }}
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        info_title = QLabel("💡 使用提示")
        info_title.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_BASE};
                font-weight: {Typography.WEIGHT_MEDIUM};
                margin-bottom: {Spacing.XS};
            }}
        """)
        
        info_text = QLabel(
            "• 选择「继续会话」可以与 AI 进行多轮对话，适合复杂任务\n"
            "• 选择「完成任务」让 AI 执行当前指令后结束，节省 API 调用\n"
            "• 你的选择将影响 AI 的后续行为和资源消耗"
        )
        info_text.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_SM};
                line-height: {Typography.LEADING_RELAXED};
            }}
        """)
        info_text.setWordWrap(True)
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_container)
    
    def _connect_signals(self) -> None:
        """连接信号"""
        self.button_group.buttonClicked.connect(self._on_state_changed)
    
    def _on_state_changed(self, button) -> None:
        """处理状态改变"""
        state_value = button.property("session_state")
        if state_value:
            self._current_state = SessionState(state_value)
            self.state_changed.emit(state_value)
    
    def get_current_state(self) -> SessionState:
        """获取当前会话状态"""
        return self._current_state
    
    def set_state(self, state: SessionState) -> None:
        """设置会话状态"""
        self._current_state = state
        
        # 更新 UI 状态
        for button in self.button_group.buttons():
            if button.property("session_state") == state.value:
                button.setChecked(True)
                break
    
    def get_state_description(self) -> str:
        """获取当前状态的描述"""
        descriptions = {
            SessionState.CONTINUE: "AI 将继续等待你的指令",
            SessionState.TERMINATE: "AI 将完成任务后结束会话",
            SessionState.PAUSE: "会话已暂停，可稍后继续"
        }
        return descriptions.get(self._current_state, "未知状态")
