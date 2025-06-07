# Interactive Feedback MCP UI - 现代化用户界面
#
# 原始项目: https://github.com/poliva/interactive-feedback-mcp
# 原作者: Fábio Ferreira & Pau Oliva
#
# === UI/UX 重大改进 ===
# 本模块在原项目基础上进行了全面的界面和体验优化:
#
# 🎨 视觉设计改进:
#   - 现代化深色主题，符合开发者使用习惯
#   - 优化的布局和间距，提升视觉舒适度
#   - 响应式设计，适配不同屏幕尺寸
#   - 精美的图标和视觉元素
#
# ⚡ 功能增强:
#   - 集成智能提示词增强功能
#   - 流式文本生成，实时显示优化过程
#   - 灵活的会话控制机制
#   - 上下文感知处理
#
# 🔧 技术优化:
#   - 基于 PySide6 的现代化 Qt 界面
#   - 异步处理，避免界面冻结
#   - 完善的错误处理和用户提示
#   - 模块化设计，易于维护和扩展
#
# 🚀 用户体验:
#   - 直观的操作流程
#   - 快速的响应速度
#   - 友好的错误提示
#   - 键盘快捷键支持
import os
import sys
import json
import argparse
import base64
from io import BytesIO # Though QBuffer might be more direct for QImage
from typing import Optional, TypedDict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QGroupBox,
    QFrame, QSpacerItem, QSizePolicy, QRadioButton, QFileDialog, QMessageBox,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QSettings, QSize, QBuffer, QIODevice, QMimeData
from PySide6.QtGui import QTextCursor, QIcon, QKeyEvent, QPalette, QColor, QPixmap, QImage, QPainter, QKeySequence
from PySide6.QtSvg import QSvgRenderer

# Import enhanced components and styles
try:
    from .prompt_enhancer import enhance_prompt_with_gemini
    from .ui_styles import Colors, Typography, Spacing, ComponentStyles, get_application_style
    from .session_control import SessionControlWidget, SessionState
    from .prompt_enhancement_widget import PromptEnhancementWidget
except ImportError:
    # Fallback for when running as main module
    try:
        from prompt_enhancer import enhance_prompt_with_gemini
        from ui_styles import Colors, Typography, Spacing, ComponentStyles, get_application_style
        from session_control import SessionControlWidget, SessionState
        from prompt_enhancement_widget import PromptEnhancementWidget
    except ImportError:
        enhance_prompt_with_gemini = None
        # 如果无法导入新组件，使用原始样式
        class Colors:
            BACKGROUND = "#0a0a0a"
            TEXT_PRIMARY = "#fafafa"
            PRIMARY = "#4a9eff"

        class ComponentStyles:
            @staticmethod
            def button_primary():
                return ""

        def get_application_style():
            return ""

        SessionControlWidget = None
        PromptEnhancementWidget = None

# Feature flag for image upload functionality
ENABLE_IMAGE_UPLOAD = True  # Enabled - integrated clipboard paste and file upload functionality

# Define the theme color and stylesheet
# Original THEME_COLOR = "#007bff"
# Original HOVER_COLOR = "#0056b3"
# Original PRESSED_COLOR = "#004085"

# New black theme for checkbox to align with overall B&W style
CHECKBOX_CHECKED_COLOR = "#2BBE6C"            # Green background for checked state
CHECKBOX_CHECKED_HOVER_COLOR = "#26a360"       # Darker green for hover on checked state

# New theme for black and white style
THEME_COLOR = "#000000"                 # Main theme color for buttons (black)
HOVER_COLOR = "#1A1A1A"                 # Hover color for buttons (dark gray)
PRESSED_COLOR = "#0A0A0A"               # Pressed color for buttons (very dark gray)

# Font size standards for consistency
FONT_SIZE_LARGE = "16px"               # For main headings and important text
FONT_SIZE_MEDIUM = "14px"              # For regular text and buttons
FONT_SIZE_SMALL = "12px"               # For secondary text and context info

BACKGROUND_COLOR = "#2c3e50"
BASE_COLOR = "#34495e" 
INPUT_BACKGROUND_COLOR = "#282828" 
TEXT_COLOR_PRIMARY = "#f0f0f0"
TEXT_COLOR_SECONDARY = "#e0e0e0"
BORDER_COLOR = "#4a4a4a"
PLACEHOLDER_COLOR_HEX = "#a0a0a0" # Used for palette
INPUT_FOCUS_BORDER_COLOR = "#6a737c" # Neutral gray for input focus

MODERN_STYLESHEET = f"""
QMainWindow {{
    background: transparent; /* Necessary for WA_TranslucentBackground */
}}

QGroupBox {{
    font-weight: bold;
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    margin-top: 12px; /* Increased slightly for title spacing */
    padding-top: 10px; /* Space for the title inside the border */
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 2px 8px; /* Vertical and horizontal padding */
    color: {TEXT_COLOR_SECONDARY};
    font-size: {FONT_SIZE_MEDIUM};
    font-weight: bold;
    /* background-color: {BASE_COLOR}; Optional: if title needs a distinct background */
    /* border-radius: 4px; Optional: if title background has radius */
}}

QLabel {{
    color: {TEXT_COLOR_SECONDARY};
    padding: 2px;
}}

QPushButton {{
    background-color: {THEME_COLOR};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 5px;
    font-size: {FONT_SIZE_MEDIUM};
}}

QPushButton:hover {{
    background-color: {HOVER_COLOR};
}}

QPushButton:pressed {{
    background-color: {PRESSED_COLOR};
}}

QTextEdit {{ /* Affects FeedbackTextEdit */
    background-color: {INPUT_BACKGROUND_COLOR}; /* Changed to new input background color */
    color: {TEXT_COLOR_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 5px;
    padding: 5px;
    /* qproperty-alignment: AlignCenter; Removed as it had no effect on QTextEdit placeholder */
}}

QTextEdit:focus {{
    border: 1px solid {INPUT_FOCUS_BORDER_COLOR};
}}

QCheckBox {{
    spacing: 8px; /* Increased spacing */
    color: {TEXT_COLOR_SECONDARY};
    padding: 4px 0;
}}

QCheckBox::indicator {{
    width: 12px; /* Adjusted size - smaller again */
    height: 12px; /* Adjusted size - smaller again */
    border-radius: 6px; /* Circular indicator - smaller again */
    border: 1px solid {BORDER_COLOR};
}}

QCheckBox::indicator:unchecked {{
    background-color: {INPUT_BACKGROUND_COLOR}; /* Changed to match new input background */
    border: 1px solid {BORDER_COLOR};
}}

QCheckBox::indicator:unchecked:hover {{
    border: 1px solid {BORDER_COLOR}; /* Keep border same as non-hovered, instead of THEME_COLOR */
}}

QCheckBox::indicator:checked {{
    background-color: {CHECKBOX_CHECKED_COLOR};
    border: 1px solid {CHECKBOX_CHECKED_COLOR};
    image: url(assets/checkbox_check.svg); /* Restored SVG icon */
}}

QCheckBox::indicator:checked:hover {{
    background-color: {CHECKBOX_CHECKED_HOVER_COLOR};
    border: 1px solid {CHECKBOX_CHECKED_HOVER_COLOR};
}}

QFrame[frameShape="HLine"] {{
    border: none;
    border-bottom: 1px solid {BORDER_COLOR};
    height: 1px;
    margin-top: 5px;
    margin-bottom: 5px;
}}

/* Added styles for QRadioButton */
QRadioButton {{
    spacing: 8px;
    color: {TEXT_COLOR_SECONDARY};
    padding: 4px 0;
}}

QRadioButton::indicator {{
    width: 12px;
    height: 12px;
    border-radius: 6px; /* Circular */
    border: 1px solid {BORDER_COLOR};
}}

QRadioButton::indicator:unchecked {{
    background-color: {INPUT_BACKGROUND_COLOR};
    border: 1px solid {BORDER_COLOR};
}}

QRadioButton::indicator:unchecked:hover {{
    border: 1px solid {HOVER_COLOR}; /* Slightly darker for hover */
}}

QRadioButton::indicator:checked {{
    background-color: {CHECKBOX_CHECKED_COLOR};
    border: 1px solid {CHECKBOX_CHECKED_COLOR};
    image: url(assets/checkbox_check.svg); /* Use checkbox_check.svg for radio button as well */
}}

QRadioButton::indicator:checked:hover {{
    background-color: {CHECKBOX_CHECKED_HOVER_COLOR};
    border: 1px solid {CHECKBOX_CHECKED_HOVER_COLOR};
}}

QLabel#imagePreviewLabel {{
    border: 1px solid {BORDER_COLOR};
    min-height: 100px; /* Example size */
    max-height: 200px;
    margin-top: 5px;
    margin-bottom: 5px;
    alignment: 'AlignCenter'; /* Not a direct CSS property, set via setAlignment */
}}
"""

class ImagePayload(TypedDict):
    bytesBase64Encoded: str
    mimeType: str

class FeedbackResult(TypedDict):
    interactive_feedback: str
    session_control: str
    images: List[ImagePayload] # Changed from single image to list of images

def get_dark_mode_palette(app: QApplication):
    darkPalette = app.palette()
    darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ToolTipText, Qt.white)
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.Button, QColor(53, 53, 53)) # Will be overridden by stylesheet for specific QPushButtons
    darkPalette.setColor(QPalette.ButtonText, Qt.white) # Will be overridden
    darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.BrightText, Qt.red)
    darkPalette.setColor(QPalette.Link, QColor(42, 130, 218)) # Could use THEME_COLOR
    darkPalette.setColor(QPalette.Highlight, QColor(THEME_COLOR)) # Use THEME_COLOR for highlight
    darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    darkPalette.setColor(QPalette.HighlightedText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
    # Adjusted placeholder text color as per plan
    darkPalette.setColor(QPalette.PlaceholderText, QColor(PLACEHOLDER_COLOR_HEX))
    return darkPalette

class FeedbackTextEdit(QTextEdit):
    # 图片处理常量
    DEFAULT_MAX_IMAGE_WIDTH = 1624
    DEFAULT_MAX_IMAGE_HEIGHT = 1624
    DEFAULT_IMAGE_FORMAT = "PNG"

    # 定义类级别的信号
    image_pasted = Signal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enhance_button = None
        self.image_data = []   # 保存图片的Base64数据列表
        # 获取设备的像素比例
        self.device_pixel_ratio = QApplication.primaryScreen().devicePixelRatio()
        # 图片压缩参数
        self.max_image_width = self.DEFAULT_MAX_IMAGE_WIDTH  # 最大宽度
        self.max_image_height = self.DEFAULT_MAX_IMAGE_HEIGHT  # 最大高度
        self.image_format = self.DEFAULT_IMAGE_FORMAT  # 图片格式

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            # Find the parent FeedbackUI instance and call submit
            parent = self.parent()
            while parent and not isinstance(parent, FeedbackUI):
                parent = parent.parent()
            if parent:
                parent._submit_feedback()
        else:
            super().keyPressEvent(event)

    def _convert_image_to_base64(self, image):
        """将图片转换为 Base64 编码字符串"""
        try:
            # 将图片转换为QPixmap
            if not isinstance(image, QPixmap):
                pixmap = QPixmap.fromImage(image)
            else:
                pixmap = image

            # 创建字节缓冲区
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)

            pixmap.save(buffer, self.image_format)
            file_extension = self.image_format.lower()  # 使用小写的格式名作为扩展名

            # 获取字节数据并转换为base64
            byte_array = buffer.data()
            base64_string = base64.b64encode(byte_array).decode('utf-8')
            buffer.close()

            # 返回Base64数据和文件扩展名
            return {
                'data': base64_string,
                'extension': file_extension
            }
        except Exception as e:
            print(f"转换图片为Base64时出错: {e}")
            return None

    def insertFromMimeData(self, source_data):
        """
        Handle pasting from mime data, explicitly checking for image data.
        支持视网膜屏幕(Retina Display)的高DPI显示
        """
        try:
            if source_data.hasImage():
                # If the mime data contains an image, convert to Base64
                image = source_data.imageData()
                if image:
                    try:
                        # 使用原始图片，不进行压缩
                        # 转换图片为Base64编码
                        image_result = self._convert_image_to_base64(image)

                        if image_result:
                            # 生成唯一的文件名用于标识
                            import datetime
                            import uuid
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            unique_id = str(uuid.uuid4())[:8]
                            filename = f"pasted_image_{timestamp}_{unique_id}.{image_result['extension']}"

                            # 保存Base64数据
                            image_info = {
                                'base64': image_result['data'],
                                'filename': filename
                            }
                            self.image_data.append(image_info)

                            # 发出信号，通知上层组件有新图片被粘贴
                            if isinstance(image, QPixmap):
                                pixmap = image
                            else:
                                pixmap = QPixmap.fromImage(image)
                            self.image_pasted.emit(pixmap)

                    except Exception as e:
                        print(f"处理图片时出错: {e}")
                        cursor = self.textCursor()
                        cursor.insertText(f"[图片处理失败: {str(e)}]")
                else:
                    cursor = self.textCursor()
                    cursor.insertText("[图片处理失败: 无效的图片数据]")
            elif source_data.hasHtml():
                # If the mime data contains HTML, insert it as HTML
                super().insertFromMimeData(source_data)
            elif source_data.hasText():
                # If the mime data contains plain text, insert it as plain text
                super().insertFromMimeData(source_data)
            else:
                # For other types, call the base class method
                super().insertFromMimeData(source_data)
        except Exception as e:
            print(f"处理粘贴内容时出错: {e}")
            # 尝试使用基类方法处理
            try:
                super().insertFromMimeData(source_data)
            except:
                cursor = self.textCursor()
                cursor.insertText(f"[粘贴内容失败: {str(e)}]")

    def get_image_data(self):
        """返回图片数据列表（包含Base64编码）"""
        return self.image_data.copy()

    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        if event:  # Only call super if event is not None
            super().resizeEvent(event)

class FeedbackUI(QMainWindow):
    def __init__(self, prompt: str, predefined_options: Optional[List[str]] = None, context_info: str = ""):
        super().__init__()
        self.prompt = prompt
        self.predefined_options = predefined_options or []
        # 图片上传功能完全由内部控制，基于 ENABLE_IMAGE_UPLOAD 常量
        self.enable_image_upload = ENABLE_IMAGE_UPLOAD
        self.context_info = context_info
        self.image_payloads: List[ImagePayload] = [] # For storing list of {"bytesBase64Encoded": "...", "mimeType": "..."}

        self.feedback_result = None
        
        self.setWindowTitle("Developer Feedback")
        self.setGeometry(100, 100, 800, 750)

        # Set a consistent dark background for the main window
        self.setStyleSheet(f"QMainWindow {{ background-color: {BACKGROUND_COLOR}; }}")

        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")
        
        # Load general UI settings for the main window (geometry, state)
        self.settings.beginGroup("MainWindow_General")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(800, 1000)
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - 800) // 2
            y = (screen.height() - 1000) // 2
            self.move(x, y)

        # Set minimum width to ensure stable layout
        # 根据用户反馈调整最小宽度为500，提供更好的显示效果
        self.setMinimumWidth(500)
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
        self.settings.endGroup() # End "MainWindow_General" group

        self._create_ui()
        self.setAcceptDrops(True) # Allow drag and drop events if we want to implement that later (optional)
        
        # Apply the stylesheet to the main window and its children
        self.setStyleSheet(MODERN_STYLESHEET)

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Brand Assets Section --- 
        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(0, 0, 0, 10) 

        brand_layout.addStretch(1)

        icon_label = QLabel()
        icon_pixmap = QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Icon.jpeg"))
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaledToHeight(32, Qt.SmoothTransformation))
        brand_layout.addWidget(icon_label)

        brand_layout.addSpacing(10)

        logo_label = QLabel()
        svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Logo.svg")
        renderer = QSvgRenderer(svg_path)
        if renderer.isValid():
            size = renderer.defaultSize()
            if size.height() > 0: # Avoid division by zero
                scaled_width = int(size.width() * (32 / size.height()))
                pixmap = QPixmap(scaled_width, 32)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                logo_label.setPixmap(pixmap)
        brand_layout.addWidget(logo_label)
        brand_layout.addStretch(1)
        main_layout.addLayout(brand_layout)

        # --- Context Information and Prompt Section (Side by Side) ---
        # Create horizontal layout for context and prompt panels
        context_prompt_layout = QHBoxLayout()

        # --- Context Information Section (Left Panel - 50% width) ---
        if self.context_info and self.context_info.strip():
            context_group = QGroupBox(self.tr("项目上下文信息"))
            context_layout = QVBoxLayout(context_group)

            # Create a scroll area for the context info
            context_scroll_area = QScrollArea()
            context_scroll_area.setWidgetResizable(True)
            context_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            context_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            context_scroll_area.setMaximumHeight(400)  # Increased height for better visibility (2x original)

            # Filter markdown symbols from context info text
            filtered_context_info = self._filter_markdown_symbols(self.context_info)

            # Create the context label with medium font (same as prompt)
            context_label = QLabel(filtered_context_info)
            context_label.setWordWrap(True)
            context_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            context_label.setStyleSheet(f"QLabel {{ color: #e0e0e0; font-size: {FONT_SIZE_MEDIUM}; margin: 5px; padding: 5px; }}")  # Medium font for context (same as prompt)

            # Set the label as the scroll area's widget
            context_scroll_area.setWidget(context_label)

            # Style the scroll area
            context_scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 5px;
                    background-color: {INPUT_BACKGROUND_COLOR};
                    margin-bottom: 10px;
                }}
                QScrollBar:vertical {{
                    background-color: {INPUT_BACKGROUND_COLOR};
                    width: 12px;
                    border-radius: 6px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {BORDER_COLOR};
                    border-radius: 6px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {TEXT_COLOR_SECONDARY};
                }}
            """)

            context_layout.addWidget(context_scroll_area)
            context_prompt_layout.addWidget(context_group)  # Add to horizontal layout

        # --- Prompt Section (Right Panel - 50% width) ---
        prompt_group = QGroupBox(self.tr("AI 摘要信息"))
        prompt_layout = QVBoxLayout(prompt_group)

        # Create a scroll area for the prompt
        prompt_scroll_area = QScrollArea()
        prompt_scroll_area.setWidgetResizable(True)
        prompt_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        prompt_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        prompt_scroll_area.setMaximumHeight(400)  # Further increased height to show more content

        # Filter markdown symbols from prompt text
        filtered_prompt = self._filter_markdown_symbols(self.prompt)

        # Create the prompt label with medium font
        prompt_label = QLabel(filtered_prompt)
        prompt_label.setWordWrap(True)
        prompt_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        prompt_label.setStyleSheet(f"QLabel {{ color: #f0f0f0; font-size: {FONT_SIZE_MEDIUM}; margin: 5px; padding: 5px; }}")  # Standard medium font

        # Set the label as the scroll area's widget
        prompt_scroll_area.setWidget(prompt_label)

        # Style the scroll area
        prompt_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                background-color: {INPUT_BACKGROUND_COLOR};
                margin-bottom: 10px;
            }}
            QScrollBar:vertical {{
                background-color: {INPUT_BACKGROUND_COLOR};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {BORDER_COLOR};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {TEXT_COLOR_SECONDARY};
            }}
        """)

        prompt_layout.addWidget(prompt_scroll_area)
        context_prompt_layout.addWidget(prompt_group)  # Add to horizontal layout

        # Add the horizontal layout to main layout
        main_layout.addLayout(context_prompt_layout)

        # --- Image Upload Section (conditionally added) ---
        if self.enable_image_upload:
            image_upload_group = QGroupBox(self.tr("上传图片 (可选)"))
            image_upload_layout = QVBoxLayout(image_upload_group)

            # Create scroll area for image previews
            self.image_scroll_area = QScrollArea()
            self.image_scroll_area.setWidgetResizable(True)
            self.image_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.image_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.image_scroll_area.setMaximumHeight(300)  # Increased from 200 to 300
            self.image_scroll_area.setMinimumHeight(150)  # Increased from 100 to 150

            # Create widget to hold the grid layout for image previews
            self.image_preview_widget = QWidget()
            self.image_preview_layout = QGridLayout(self.image_preview_widget)
            self.image_preview_layout.setSpacing(10)

            # Set the widget as the scroll area's content
            self.image_scroll_area.setWidget(self.image_preview_widget)

            # Style the scroll area
            self.image_scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: 1px dashed {BORDER_COLOR};
                    border-radius: 5px;
                    background-color: {INPUT_BACKGROUND_COLOR};
                }}
                QScrollBar:vertical {{
                    background-color: {INPUT_BACKGROUND_COLOR};
                    width: 12px;
                    border-radius: 6px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {BORDER_COLOR};
                    border-radius: 6px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {TEXT_COLOR_SECONDARY};
                }}
            """)

            image_upload_layout.addWidget(self.image_scroll_area)

            # Add instruction label
            self.instruction_label = QLabel(self.tr("可粘贴图片到文本框或拖拽到此区域，也可点击下方按钮选择文件上传"))
            self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.instruction_label.setStyleSheet(f"color: {TEXT_COLOR_SECONDARY}; font-size: {FONT_SIZE_SMALL}; margin: 5px;")
            image_upload_layout.addWidget(self.instruction_label)

            image_buttons_layout = QHBoxLayout()
            self.upload_image_button = QPushButton(self.tr("选择图片文件..."))
            self.upload_image_button.clicked.connect(self._handle_upload_image_file)
            image_buttons_layout.addWidget(self.upload_image_button)

            self.clear_image_button = QPushButton(self.tr("清除所有图片"))
            self.clear_image_button.clicked.connect(self._handle_clear_image)
            self.clear_image_button.setEnabled(False) # Initially disabled
            image_buttons_layout.addWidget(self.clear_image_button)
            image_upload_layout.addLayout(image_buttons_layout)

            main_layout.addWidget(image_upload_group)

            # Initialize preview area
            self._refresh_previews()

        # --- Predefined Options Section (Third Row) ---
        if self.predefined_options:
            options_group = QGroupBox(self.tr("预设选项"))
            options_layout = QVBoxLayout(options_group)

            self.checkboxes = []
            for option_text in self.predefined_options:
                checkbox = QCheckBox(option_text)
                options_layout.addWidget(checkbox)
                self.checkboxes.append(checkbox)

            main_layout.addWidget(options_group)

        # --- Session Control Section (Fourth Row) ---
        session_control_group = QGroupBox(self.tr("会话控制"))
        session_control_layout = QHBoxLayout(session_control_group)

        self.continue_session_radio = QRadioButton(self.tr("继续会话 (Continue Session)"))
        self.terminate_session_radio = QRadioButton(self.tr("终止会话 (Terminate Session)"))
        self.continue_session_radio.setChecked(True)

        # Add spacer to center the radio buttons horizontally
        session_control_layout.addStretch(1)
        session_control_layout.addWidget(self.continue_session_radio)
        session_control_layout.addWidget(self.terminate_session_radio)
        session_control_layout.addStretch(1)

        main_layout.addWidget(session_control_group)

        # --- Feedback Text Input Section with Embedded Button (Fifth Row) ---
        # Create a container widget for the text input and button
        feedback_container = QWidget()
        feedback_container_layout = QVBoxLayout(feedback_container)
        feedback_container_layout.setContentsMargins(0, 0, 0, 0)

        # Create the text input
        self.feedback_text = FeedbackTextEdit()
        self.feedback_text.setPlaceholderText(self.tr("请在此输入您的反馈... (支持粘贴图片，点击右上角魔法图标优化提示词)"))

        # Connect image pasted signal if image upload is enabled
        if self.enable_image_upload:
            self.feedback_text.image_pasted.connect(self._on_image_pasted_to_text)

        # Set reduced height (1/2 of original) and styling with padding for button
        self.feedback_text.setMaximumHeight(100)  # Reduced height to about 1/2
        self.feedback_text.setMinimumHeight(60)   # Set minimum height
        self.feedback_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {INPUT_BACKGROUND_COLOR};
                color: {TEXT_COLOR_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 5px 40px 5px 5px;  /* Add right padding for button */
                font-size: {FONT_SIZE_MEDIUM};
            }}
            QTextEdit:focus {{
                border: 1px solid {INPUT_FOCUS_BORDER_COLOR};
            }}
        """)

        # Create the enhancement button (icon only)
        self.enhance_prompt_button = QPushButton(feedback_container)
        self.enhance_prompt_button.setToolTip(self.tr("优化提示词 - 将简单想法转化为详细、结构化的描述"))

        # Set up the magic icon only (no text)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        magic_icon_path = os.path.join(script_dir, "assets", "magic.svg")

        if os.path.exists(magic_icon_path):
            enhance_icon = QIcon(magic_icon_path)
            self.enhance_prompt_button.setIcon(enhance_icon)
            self.enhance_prompt_button.setText("")  # No text, icon only
        else:
            self.enhance_prompt_button.setText("✨")  # Fallback with emoji only

        # Style the button with black background
        self.enhance_prompt_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
                padding: 4px;
                width: 24px;
                height: 24px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};
                border: 1px solid {TEXT_COLOR_SECONDARY};
            }}
            QPushButton:pressed {{
                background-color: {PRESSED_COLOR};
            }}
        """)

        # Set button size and position it in the top-right corner of text input
        self.enhance_prompt_button.setFixedSize(24, 24)

        # Connect button click to handler
        self.enhance_prompt_button.clicked.connect(self._handle_enhance_prompt)

        # Add text input to container
        feedback_container_layout.addWidget(self.feedback_text)

        # Position the button in the top-right corner using absolute positioning
        def position_button():
            button_x = self.feedback_text.width() - self.enhance_prompt_button.width() - 10
            button_y = 5  # Move button higher up
            self.enhance_prompt_button.move(button_x, button_y)
            self.enhance_prompt_button.raise_()  # Bring button to front

        # Connect resize event to reposition button
        original_resize_event = self.feedback_text.resizeEvent
        def on_feedback_resize(event):
            original_resize_event(event)  # Call original resize event first
            if event:
                position_button()

        self.feedback_text.resizeEvent = on_feedback_resize

        # Initial positioning
        QTimer.singleShot(0, position_button)

        main_layout.addWidget(feedback_container)

        # --- Submit Button Section ---
        submit_button_layout = QHBoxLayout()
        submit_button_layout.addStretch(1)
        self.submit_button = QPushButton()
        if sys.platform == "darwin": # macOS
            self.submit_button.setText(self.tr("提交反馈 (⌘+Enter)"))
        else: # Windows/Linux
            # As per plan, keeping Ctrl+Enter for other OS, or could be generic
            self.submit_button.setText(self.tr("提交反馈 (Ctrl+Enter)")) 
        self.submit_button.clicked.connect(self._submit_feedback)
        submit_button_layout.addWidget(self.submit_button)
        submit_button_layout.addStretch(1)
        main_layout.addLayout(submit_button_layout)

        # Add some spacing at the bottom, if still desired after removing footer
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Apply the stylesheet AFTER all widgets are created and parented to the central_widget or its children
        central_widget.setStyleSheet(MODERN_STYLESHEET)

    def _filter_markdown_symbols(self, text: str) -> str:
        """
        过滤文本中的Markdown符号，使其适合在QLabel中显示
        根据用户需求，只移除加粗符号，保留其他内容如代码块等

        Args:
            text: 原始文本

        Returns:
            过滤后的文本
        """
        if not text:
            return text

        # 只移除加粗符号，保留其他格式内容
        filtered_text = text

        # 移除加粗符号 **text** 和 __text__
        import re
        filtered_text = re.sub(r'\*\*(.*?)\*\*', r'\1', filtered_text)
        filtered_text = re.sub(r'__(.*?)__', r'\1', filtered_text)

        return filtered_text.strip()

    def _refresh_previews(self):
        """刷新图片预览区域，根据 image_payloads 列表动态创建缩略图"""
        # Clear existing previews
        while self.image_preview_layout.count():
            child = self.image_preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.image_payloads:
            # Show placeholder when no images
            placeholder_label = QLabel(self.tr("暂无图片，可拖拽或粘贴图片到此区域"))
            placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder_label.setStyleSheet(f"color: {TEXT_COLOR_SECONDARY}; font-style: italic; padding: 20px;")
            self.image_preview_layout.addWidget(placeholder_label, 0, 0)
            return

        # Create thumbnails for each image
        max_columns = 3  # Maximum images per row
        for index, image_payload in enumerate(self.image_payloads):
            row = index // max_columns
            col = index % max_columns

            # Create frame for each image thumbnail
            image_frame = QFrame()
            image_frame.setFrameStyle(QFrame.Box)

            # Set fixed width for image frames to ensure 1/3 width when single image
            frame_width = 200  # Fixed width for each image frame
            image_frame.setFixedWidth(frame_width)

            image_frame.setStyleSheet(f"""
                QFrame {{
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 5px;
                    background-color: {INPUT_BACKGROUND_COLOR};
                    padding: 5px;
                }}
            """)

            frame_layout = QVBoxLayout(image_frame)
            frame_layout.setSpacing(5)

            # Create thumbnail image
            try:
                import base64
                image_data = base64.b64decode(image_payload["bytesBase64Encoded"])
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)

                if not pixmap.isNull():
                    # Scale to thumbnail size
                    thumbnail_size = 80
                    scaled_pixmap = pixmap.scaled(
                        thumbnail_size, thumbnail_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )

                    image_label = QLabel()
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    frame_layout.addWidget(image_label)
                else:
                    # Fallback for invalid image data
                    error_label = QLabel(self.tr("图片加载失败"))
                    error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    error_label.setStyleSheet(f"color: {TEXT_COLOR_SECONDARY}; font-size: {FONT_SIZE_SMALL};")
                    frame_layout.addWidget(error_label)

            except Exception as e:
                # Error handling for image processing
                error_label = QLabel(self.tr("图片处理错误"))
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_label.setStyleSheet(f"color: {TEXT_COLOR_SECONDARY}; font-size: {FONT_SIZE_SMALL};")
                frame_layout.addWidget(error_label)

            # Add delete button
            delete_button = QPushButton(self.tr("删除"))
            delete_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: {FONT_SIZE_SMALL};
                }}
                QPushButton:hover {{
                    background-color: #c82333;
                }}
                QPushButton:pressed {{
                    background-color: #bd2130;
                }}
            """)
            delete_button.clicked.connect(lambda checked=False, idx=index: self._handle_remove_image(idx))
            frame_layout.addWidget(delete_button)

            # Add frame to grid layout
            self.image_preview_layout.addWidget(image_frame, row, col)

        # Update clear button state
        if hasattr(self, 'clear_image_button'):
            self.clear_image_button.setEnabled(len(self.image_payloads) > 0)

    def _handle_remove_image(self, image_index: int):
        """根据索引从 image_payloads 列表中移除图片，并刷新UI"""
        if 0 <= image_index < len(self.image_payloads):
            self.image_payloads.pop(image_index)
            self._refresh_previews()

    def _on_image_pasted_to_text(self, pixmap):
        """处理从文本框粘贴的图片"""
        # 将QPixmap转换为QImage
        qimage = pixmap.toImage()
        if not qimage.isNull():
            # 使用统一的图片添加方法
            self._add_image_from_qimage(qimage, "pasted_image")

    def _add_image_from_qimage(self, qimage: QImage, source_name: str = "image"):
        """从QImage添加图片到payloads列表"""
        try:
            # 转换为Base64
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)

            # 保存为PNG格式以保持质量
            if not qimage.save(buffer, "PNG"):
                print("Error: Could not save image to buffer.")
                return

            image_bytes = buffer.data()
            base64_encoded_data = base64.b64encode(image_bytes).decode('utf-8')

            # 创建图片载荷
            new_payload = {
                "bytesBase64Encoded": base64_encoded_data,
                "mimeType": "image/png"
            }
            self.image_payloads.append(new_payload)

            # 刷新预览
            self._refresh_previews()

        except Exception as e:
            print(f"添加图片时出错: {e}")

    def _stream_enhance_text(self, original_text: str):
        """
        流式增强文本，逐步返回生成的内容块

        Args:
            original_text: 原始文本

        Yields:
            str: 文本块
        """
        try:
            from prompt_enhancer import enhance_prompt_with_gemini_stream_generator

            # 调用流式生成器，传递上下文信息
            for chunk in enhance_prompt_with_gemini_stream_generator(original_text, self.context_info):
                yield chunk

        except ImportError:
            # 如果没有流式生成器，回退到普通方式
            from prompt_enhancer import enhance_prompt_with_gemini
            result = enhance_prompt_with_gemini(original_text, self.context_info)
            yield result

    def _submit_feedback(self):
        feedback_text = self.feedback_text.toPlainText().strip()
        selected_options = []
        
        # Corrected to use self.checkboxes as defined in _create_ui
        if hasattr(self, 'checkboxes') and self.checkboxes:
            for checkbox in self.checkboxes:
                if checkbox.isChecked():
                    # Make sure to get the text from the checkbox itself
                    selected_options.append(checkbox.text())
        
        # Combine selected options and feedback text
        final_feedback_parts = []
        
        # Add selected options
        if selected_options:
            final_feedback_parts.append("; ".join(selected_options))
        
        # Add user's text feedback
        if feedback_text:
            final_feedback_parts.append(feedback_text)
            
        # Join with a newline if both parts exist
        final_feedback = "\n\n".join(final_feedback_parts)

        # 路径识别与替换
        import re
        def format_paths(text):
            parts = re.split(r'(\s+)', text)
            for i, part in enumerate(parts):
                if not (part is None or re.match(r'^\s*$', part)): # if it's not a whitespace part
                    if ('/' in part or '\\' in part) and not (part.startswith('http://') or part.startswith('https://')):
                        # 避免重复格式化
                        if not part.startswith('用户提供文件路径："') and not part.startswith('用户提供文件路径："'):
                            parts[i] = f'用户提供文件路径："{part}"'
            return "".join(parts)
        
        final_feedback = format_paths(final_feedback)
            
        # Determine session control value
        session_control_value = "continue" # Default to continue, as per new UI default
        if hasattr(self, 'terminate_session_radio') and self.terminate_session_radio.isChecked():
            session_control_value = "terminate"
        elif hasattr(self, 'continue_session_radio') and self.continue_session_radio.isChecked():
            session_control_value = "continue"
        # If neither somehow (should not happen with radio buttons), it defaults to continue

        result_dict = {
            "interactive_feedback": final_feedback,
            "session_control": session_control_value
        }
        # Always include images list if image upload is enabled
        if self.enable_image_upload:
            # 合并来自文件上传和文本框粘贴的图片
            all_images = self.image_payloads.copy()

            # 添加来自文本框粘贴的图片
            text_images = self.feedback_text.get_image_data()
            for img_data in text_images:
                # 转换格式以匹配现有结构
                image_payload = {
                    "bytesBase64Encoded": img_data['base64'],
                    "mimeType": f"image/{img_data.get('extension', 'png')}"
                }
                all_images.append(image_payload)

            result_dict["images"] = all_images

        # Cast to FeedbackResult for type hinting, though it's a dict at runtime for JSON
        self.feedback_result = FeedbackResult(**result_dict)
        self.close()

    def _handle_enhance_prompt(self):
        """处理提示词增强按钮点击事件"""
        # 检查是否有增强服务可用
        if enhance_prompt_with_gemini is None:
            QMessageBox.warning(
                self,
                self.tr("功能不可用"),
                self.tr("提示词增强功能不可用。请确保已安装 google-genai 依赖包。")
            )
            return

        # 获取当前文本
        original_text = self.feedback_text.toPlainText().strip()
        if not original_text:
            QMessageBox.information(
                self,
                self.tr("提示"),
                self.tr("请先输入一些文本，然后再使用提示词增强功能。")
            )
            return

        # 禁用按钮并显示处理状态
        self.enhance_prompt_button.setEnabled(False)
        original_text_button = self.enhance_prompt_button.text()
        self.enhance_prompt_button.setText(self.tr("优化中..."))
        QApplication.processEvents()  # 确保UI更新

        try:
            # 清空文本框，准备流式显示
            self.feedback_text.setPlainText("")

            # 调用流式增强服务
            from prompt_enhancer import enhance_prompt_with_gemini_stream

            # 使用流式方式逐步显示内容
            enhanced_text = ""
            for chunk in self._stream_enhance_text(original_text):
                if chunk.startswith("错误："):
                    QMessageBox.warning(
                        self,
                        self.tr("增强失败"),
                        chunk
                    )
                    # 恢复原始文本
                    self.feedback_text.setPlainText(original_text)
                    return
                else:
                    enhanced_text += chunk
                    self.feedback_text.setPlainText(enhanced_text)
                    QApplication.processEvents()  # 确保UI实时更新

            if enhanced_text:
                QMessageBox.information(
                    self,
                    self.tr("增强完成"),
                    self.tr("提示词已成功增强！您可以查看并编辑增强后的内容。")
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("增强失败"),
                self.tr(f"提示词增强过程中发生错误：{str(e)}")
            )

        finally:
            # 恢复按钮状态
            self.enhance_prompt_button.setEnabled(True)
            self.enhance_prompt_button.setText(original_text_button)

    def closeEvent(self, event):
        # Save general UI settings for the main window (geometry, state)
        self.settings.beginGroup("MainWindow_General")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.endGroup()

        super().closeEvent(event)

    def run(self) -> FeedbackResult:
        self.show()
        QApplication.instance().exec()

        if not self.feedback_result:
            # Return with empty feedback and no images if window closed without submitting
            return FeedbackResult(interactive_feedback="", session_control="terminate", images=[])

        return self.feedback_result

    def _handle_upload_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("选择图片"),
            "", # Start directory
            self.tr("图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)")
        )
        if file_path:
            qimage = QImage(file_path)
            if not qimage.isNull():
                self._add_image_payload(qimage, file_path)
            else:
                # Optional: Show an error message to the user
                print(f"Error: Could not load image from {file_path}")

    def _determine_mime_type(self, qimage: QImage, file_path: Optional[str] = None) -> str:
        # Try to get format from QImage description or file extension
        # QImage.format() returns an enum, not a MIME string directly.
        # QImage.text("format") might give PNG, JPEG etc.
        img_format_str = qimage.text("format")
        if not img_format_str and file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".png": img_format_str = "PNG"
            elif ext in [".jpg", ".jpeg"]: img_format_str = "JPEG"
            elif ext == ".bmp": img_format_str = "BMP"
            elif ext == ".gif": img_format_str = "GIF"

        if img_format_str:
            return f"image/{img_format_str.lower()}"
        return "image/png" # Default if undetectable, PNG is a good lossless default

    def _add_image_payload(self, qimage: QImage, file_path: Optional[str] = None):
        """添加图片载荷（从文件上传）"""
        # 使用统一的图片添加方法
        self._add_image_from_qimage(qimage, file_path or "uploaded_image")

    def _handle_clear_image(self):
        self.image_payloads.clear()  # Clear the list of image payloads
        self._refresh_previews()  # Refresh the preview area

    def keyPressEvent(self, event: QKeyEvent):
        if self.enable_image_upload and event.matches(QKeySequence.StandardKey.Paste):
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            if mime_data.hasImage():
                qimage_from_clipboard = clipboard.image() # QImage
                if not qimage_from_clipboard.isNull():
                    self._add_image_payload(qimage_from_clipboard)
                    event.accept()
                    return
        super().keyPressEvent(event) # Pass to children like FeedbackTextEdit if not handled

def feedback_ui(prompt: str, predefined_options: Optional[List[str]] = None, output_file: Optional[str] = None, context_info: str = "") -> Optional[FeedbackResult]:
    app = QApplication.instance() or QApplication()
    app.setPalette(get_dark_mode_palette(app))
    app.setStyle("Fusion")
    ui = FeedbackUI(prompt, predefined_options, context_info)
    result = ui.run()

    if output_file and result:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        # Save the result to the output file
        with open(output_file, "w") as f:
            json.dump(result, f)
        return None

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the feedback UI")
    parser.add_argument("--prompt", default="I implemented the changes you requested.", help="The prompt to show to the user")
    parser.add_argument("--predefined-options", default="", help="Pipe-separated list of predefined options (|||)")
    parser.add_argument("--output-file", help="Path to save the feedback result as JSON")
    # 图片上传功能由 ENABLE_IMAGE_UPLOAD 常量控制，不再通过命令行参数
    parser.add_argument("--context-info", default="", help="Context information including project goals, current progress, tech stack, etc.")
    args = parser.parse_args()

    predefined_options = [opt for opt in args.predefined_options.split("|||") if opt] if args.predefined_options else None

    # 图片上传功能完全由 FeedbackUI 内部的 ENABLE_IMAGE_UPLOAD 常量控制
    result = feedback_ui(
        prompt=args.prompt,
        predefined_options=predefined_options,
        output_file=args.output_file,
        context_info=args.context_info
    )
    if result:
        print(f"\nFeedback received:\n{result['interactive_feedback']}")
    sys.exit(0)
