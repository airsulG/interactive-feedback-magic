# UI Styles - shadcn/ui 风格设计系统
#
# === 设计理念 ===
# 本模块实现了受 shadcn/ui 启发的现代化设计系统
# 专为 Interactive Feedback MCP 项目定制
#
# 🎨 设计原则:
# - 简洁优雅: 去除不必要的装饰，专注于功能
# - 一致性: 统一的颜色、字体和间距系统
# - 可访问性: 良好的对比度和可读性
# - 响应式: 适配不同屏幕尺寸和分辨率
#
# 🌙 深色主题优先:
# - 减少眼部疲劳，适合长时间开发工作
# - 现代化外观，符合开发者审美
# - 节省设备电量（OLED 屏幕）

from typing import Dict, Any

# === 颜色系统 ===
# 基于 shadcn/ui 的现代化配色方案

class Colors:
    """shadcn/ui 风格配色系统"""
    
    # 主色调 - 基于深色主题
    BACKGROUND = "#0a0a0a"          # 主背景色
    SURFACE = "#1a1a1a"             # 卡片/面板背景
    SURFACE_HOVER = "#2a2a2a"       # 悬停状态
    SURFACE_ACTIVE = "#3a3a3a"      # 激活状态
    
    # 边框和分割线
    BORDER = "#2a2a2a"              # 默认边框
    BORDER_HOVER = "#3a3a3a"        # 悬停边框
    BORDER_FOCUS = "#4a9eff"        # 聚焦边框
    
    # 文本颜色
    TEXT_PRIMARY = "#fafafa"        # 主要文本
    TEXT_SECONDARY = "#a1a1aa"      # 次要文本
    TEXT_MUTED = "#71717a"          # 静音文本
    TEXT_DISABLED = "#52525b"       # 禁用文本
    
    # 主题色
    PRIMARY = "#4a9eff"             # 主要操作色
    PRIMARY_HOVER = "#3b82f6"       # 主要操作悬停
    PRIMARY_ACTIVE = "#2563eb"      # 主要操作激活
    
    # 语义色彩
    SUCCESS = "#22c55e"             # 成功状态
    SUCCESS_HOVER = "#16a34a"       # 成功悬停
    WARNING = "#f59e0b"             # 警告状态
    WARNING_HOVER = "#d97706"       # 警告悬停
    ERROR = "#ef4444"               # 错误状态
    ERROR_HOVER = "#dc2626"         # 错误悬停
    
    # 特殊用途
    ACCENT = "#8b5cf6"              # 强调色（提示词增强按钮）
    ACCENT_HOVER = "#7c3aed"        # 强调色悬停
    MAGIC = "#f97316"               # 魔法效果色（AI 功能）
    MAGIC_HOVER = "#ea580c"         # 魔法效果悬停

class Typography:
    """字体系统"""
    
    # 字体族
    FONT_FAMILY = "SF Pro Display, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    FONT_FAMILY_MONO = "SF Mono, Monaco, Consolas, Liberation Mono, Courier New, monospace"
    
    # 字体大小
    TEXT_XS = "11px"      # 极小文本
    TEXT_SM = "12px"      # 小文本
    TEXT_BASE = "14px"    # 基础文本
    TEXT_LG = "16px"      # 大文本
    TEXT_XL = "18px"      # 超大文本
    TEXT_2XL = "20px"     # 标题文本
    TEXT_3XL = "24px"     # 大标题
    
    # 字重
    WEIGHT_NORMAL = "400"
    WEIGHT_MEDIUM = "500"
    WEIGHT_SEMIBOLD = "600"
    WEIGHT_BOLD = "700"
    
    # 行高
    LEADING_TIGHT = "1.25"
    LEADING_NORMAL = "1.5"
    LEADING_RELAXED = "1.75"

class Spacing:
    """间距系统"""
    
    # 基础间距单位 (4px)
    UNIT = 4
    
    # 间距值
    XS = f"{1 * UNIT}px"      # 4px
    SM = f"{2 * UNIT}px"      # 8px
    MD = f"{3 * UNIT}px"      # 12px
    LG = f"{4 * UNIT}px"      # 16px
    XL = f"{5 * UNIT}px"      # 20px
    XXL = f"{6 * UNIT}px"     # 24px
    XXXL = f"{8 * UNIT}px"    # 32px

class BorderRadius:
    """圆角系统"""
    
    NONE = "0px"
    SM = "4px"
    MD = "6px"
    LG = "8px"
    XL = "12px"
    XXL = "16px"
    FULL = "9999px"

class Shadows:
    """阴影系统"""
    
    NONE = "none"
    SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

class ComponentStyles:
    """组件样式定义"""
    
    @staticmethod
    def button_primary() -> str:
        """主要按钮样式"""
        return f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.PRIMARY};
                border-radius: {BorderRadius.MD};
                padding: {Spacing.SM} {Spacing.LG};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_BASE};
                font-weight: {Typography.WEIGHT_MEDIUM};
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_HOVER};
                border-color: {Colors.PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY_ACTIVE};
                border-color: {Colors.PRIMARY_ACTIVE};
            }}
            QPushButton:disabled {{
                background-color: {Colors.SURFACE};
                color: {Colors.TEXT_DISABLED};
                border-color: {Colors.BORDER};
            }}
        """
    
    @staticmethod
    def button_secondary() -> str:
        """次要按钮样式"""
        return f"""
            QPushButton {{
                background-color: {Colors.SURFACE};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: {BorderRadius.MD};
                padding: {Spacing.SM} {Spacing.LG};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_BASE};
                font-weight: {Typography.WEIGHT_MEDIUM};
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_HOVER};
                border-color: {Colors.BORDER_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.SURFACE_ACTIVE};
            }}
        """
    
    @staticmethod
    def button_accent() -> str:
        """强调按钮样式（用于 AI 功能）"""
        return f"""
            QPushButton {{
                background-color: {Colors.ACCENT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.ACCENT};
                border-radius: {BorderRadius.MD};
                padding: {Spacing.SM} {Spacing.LG};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_BASE};
                font-weight: {Typography.WEIGHT_MEDIUM};
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_HOVER};
                border-color: {Colors.ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.ACCENT};
                transform: translateY(1px);
            }}
        """
    
    @staticmethod
    def text_area() -> str:
        """文本区域样式"""
        return f"""
            QTextEdit {{
                background-color: {Colors.SURFACE};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: {BorderRadius.MD};
                padding: {Spacing.MD};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_BASE};
                line-height: {Typography.LEADING_NORMAL};
                selection-background-color: {Colors.PRIMARY};
                selection-color: {Colors.TEXT_PRIMARY};
            }}
            QTextEdit:focus {{
                border-color: {Colors.BORDER_FOCUS};
                outline: none;
            }}
        """
    
    @staticmethod
    def card() -> str:
        """卡片容器样式"""
        return f"""
            QFrame {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: {BorderRadius.LG};
                padding: {Spacing.XL};
            }}
        """
    
    @staticmethod
    def radio_button() -> str:
        """单选按钮样式"""
        return f"""
            QRadioButton {{
                color: {Colors.TEXT_PRIMARY};
                font-family: {Typography.FONT_FAMILY};
                font-size: {Typography.TEXT_BASE};
                spacing: {Spacing.SM};
                padding: {Spacing.SM};
            }}
            QRadioButton:hover {{
                color: {Colors.PRIMARY};
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {Colors.BORDER};
                background-color: {Colors.SURFACE};
            }}
            QRadioButton::indicator:checked {{
                border-color: {Colors.PRIMARY};
                background-color: {Colors.PRIMARY};
            }}
            QRadioButton::indicator:hover {{
                border-color: {Colors.PRIMARY_HOVER};
            }}
        """

def get_application_style() -> str:
    """获取应用程序全局样式"""
    return f"""
        QApplication {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
            font-family: {Typography.FONT_FAMILY};
        }}
        
        QMainWindow {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
        }}
        
        QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-family: {Typography.FONT_FAMILY};
        }}
        
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        
        QScrollBar:vertical {{
            background-color: {Colors.SURFACE};
            width: 8px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {Colors.BORDER_HOVER};
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {Colors.TEXT_MUTED};
        }}
    """
