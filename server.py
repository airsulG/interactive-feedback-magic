# Interactive Feedback MCP - Enhanced Version
#
# 原始项目: https://github.com/poliva/interactive-feedback-mcp
# 原作者: Fábio Ferreira (https://x.com/fabiomlferreira) & Pau Oliva (https://x.com/pof)
# 灵感来源: Tommy Tong's interactive-mcp (https://github.com/ttommyth/interactive-mcp)
#
# === 本版本的主要改进 ===
# 🔒 安全性增强:
#   - 移除所有硬编码 API 密钥，通过环境变量安全管理
#   - 添加完整的安全检查和验证机制
#   - 优化错误处理和日志记录
#
# ⚡ 功能增强:
#   - 集成 Google Gemini API 提示词增强功能
#   - 智能会话控制机制，支持用户选择继续或终止会话
#   - 上下文感知处理，提供更精准的交互体验
#   - 流式文本生成，提升用户体验
#
# 🎨 UI/UX 改进:
#   - 现代化深色主题界面设计
#   - 优化的交互流程和响应式布局
#   - 增强的错误提示和用户引导
#
# 📋 代码质量:
#   - 完善的中文注释和文档
#   - 模块化设计和清晰的代码结构
#   - 遵循 Python 最佳实践和 MCP 规范
import os
import sys
import json
import tempfile
import subprocess
import base64
import io
from typing import Dict, List, Optional, Tuple

from fastmcp import FastMCP, Image
from pydantic import Field
from mcp.types import TextContent

try:
    from PIL import Image as PILImage
except ImportError:
    # 提供一个替代方案或明确的错误信息
    # 这样即使没有安装Pillow，服务器也能启动，只是工具不可用
    PILImage = None

# FastMCP 服务器实例
# 注意: log_level="ERROR" 是为了兼容 Cline 客户端的要求
# 参考: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

def debug_log(message: str) -> None:
    """
    调试日志函数 - 改进版本

    功能增强:
    - 双重输出: 同时输出到 stderr 和日志文件
    - 时间戳记录: 便于问题追踪和调试
    - 异常安全: 日志写入失败不影响主程序运行

    Args:
        message: 要记录的调试信息
    """
    print(f"[DEBUG] {message}", file=sys.stderr)

    # 写入日志文件，便于后续分析和调试
    try:
        with open("debug.log", "a", encoding="utf-8") as f:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        # 静默处理日志写入错误，确保主程序稳定运行
        pass

# === 图片处理功能 ===
# 重新启用图片处理功能，整合剪贴板粘贴和文件上传
#
# 功能特性:
# - 支持剪贴板粘贴图片
# - 支持文件选择上传
# - Base64编码传输，简化处理流程
# - 统一的图片数据格式

def process_images(images_data: List[Dict[str, str]]) -> List[Image]:
    """
    将包含多个图片载荷（base64编码）的列表转换为 MCP Image 对象列表

    Args:
        images_data: 包含 base64 编码图片数据的字典列表
                    格式: [{"bytesBase64Encoded": "...", "mimeType": "image/png"}, ...]

    Returns:
        转换后的 MCP Image 对象列表

    Note:
        支持剪贴板粘贴和文件上传的图片处理
    """
    debug_log(f"开始处理 {len(images_data)} 张图片")
    images = []

    for i, image_data in enumerate(images_data):
        try:
            # 获取Base64编码的图片数据
            b64_data = image_data.get("bytesBase64Encoded", "")
            mime_type = image_data.get("mimeType", "image/png")

            if not b64_data:
                debug_log(f"图片 {i+1}: Base64数据为空，跳过")
                continue

            # 解码Base64数据
            img_bytes = base64.b64decode(b64_data)
            debug_log(f"图片 {i+1}: 解码成功，大小 {len(img_bytes)} bytes，类型 {mime_type}")

            # 创建MCP Image对象
            # 从mime_type提取格式（如 "image/png" -> "png"）
            format_str = mime_type.split('/')[-1] if '/' in mime_type else "png"
            image = Image(data=img_bytes, format=format_str)
            images.append(image)

        except Exception as e:
            debug_log(f"图片 {i+1} 处理失败: {e}")
            continue

    debug_log(f"成功处理 {len(images)} 张图片")
    return images

def launch_feedback_ui(
    summary: str,
    predefinedOptions: list[str] | None = None,
    context_info: str = ""
) -> dict[str, str]:
    """
    启动交互式反馈用户界面 - 核心功能函数

    这是本项目的核心改进之一，提供了强大的人机交互能力:

    功能特性:
    - 🎨 现代化图形界面: 基于 PySide6 的深色主题 UI
    - ⚡ 智能提示词增强: 集成 Gemini API 自动优化用户输入
    - 🔄 会话控制: 用户可选择继续或终止当前交互会话
    - 📝 预设选项: 支持快速选择，提升交互效率
    - 🌍 上下文感知: 理解项目背景，提供精准建议

    Args:
        summary: 要显示给用户的主要消息内容
        predefinedOptions: 预定义的选项列表，用户可快速选择
        context_info: 项目上下文信息，帮助 AI 更好理解当前状况

    Returns:
        包含用户反馈和会话控制信息的字典:
        - "interactive_feedback": 用户的文本反馈
        - "session_control": 会话控制状态 ("continue" 或 "terminate")
        - "images": 图片数据（当前版本已禁用）

    Raises:
        Exception: 当 UI 启动失败或用户取消操作时
    """
    debug_log("=== 启动交互式反馈 UI ===")
    debug_log(f"消息摘要长度: {len(summary)} 字符")
    debug_log(f"预设选项数量: {len(predefinedOptions) if predefinedOptions else 0}")
    debug_log(f"上下文信息长度: {len(context_info)} 字符")

    # Create a temporary file for the feedback result
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    debug_log(f"创建临时文件: {output_file}")

    try:
        # Get the path to feedback_ui.py relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        feedback_ui_path = os.path.join(script_dir, "feedback_ui.py")
        debug_log(f"UI 脚本路径: {feedback_ui_path}")

        # Run feedback_ui.py as a separate process
        # NOTE: There appears to be a bug in uv, so we need
        # to pass a bunch of special flags to make this work
        args = [
            sys.executable,
            "-u",
            feedback_ui_path,
            "--prompt", summary,
            "--output-file", output_file,
            "--predefined-options", "|||".join(predefinedOptions) if predefinedOptions else "",
            "--context-info", context_info if context_info else ""
            # 图片上传功能已启用，无需禁用参数
        ]
        debug_log(f"启动 UI 进程，参数数量: {len(args)}")

        result = subprocess.run(
            args,
            check=False,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            close_fds=True,
            text=True
        )
        debug_log(f"UI 进程退出，返回码: {result.returncode}")

        # 记录标准输出和错误输出
        if result.stdout:
            debug_log(f"UI 进程标准输出: {result.stdout}")
        if result.stderr:
            debug_log(f"UI 进程错误输出: {result.stderr}")

        if result.returncode != 0:
            error_msg = f"Failed to launch feedback UI: {result.returncode}"
            if result.stderr:
                error_msg += f"\nError output: {result.stderr}"
            raise Exception(error_msg)

        # Read the result from the temporary file
        debug_log(f"读取结果文件: {output_file}")
        if not os.path.exists(output_file):
            debug_log("错误：结果文件不存在")
            raise Exception("Result file does not exist")

        file_size = os.path.getsize(output_file)
        debug_log(f"结果文件大小: {file_size} bytes")

        with open(output_file, 'r', encoding='utf-8') as f:
            result_data = json.load(f)

        debug_log(f"成功读取结果，类型: {type(result_data)}")
        if isinstance(result_data, dict):
            debug_log(f"结果键: {list(result_data.keys())}")
            images_count = len(result_data.get("images", []))
            debug_log(f"结果中包含图片数量: {images_count}")

        os.unlink(output_file)
        debug_log("临时文件已删除")
        return result_data

    except Exception as e:
        debug_log(f"启动 UI 时发生错误: {e}")
        if os.path.exists(output_file):
            debug_log("清理临时文件")
            os.unlink(output_file)
        raise e
    
@mcp.tool()
def interactive_feedback(
    message: str = Field(description="The specific question for the user"),
    predefined_options: list = Field(default=None, description="Predefined options for the user to choose from (optional)"),
    context_info: str = Field(default="", description="Context information including project goals, current progress, tech stack, etc. (optional)"),
) -> Tuple[str | Image, ...]:
    """
    交互式反馈工具 - MCP 核心工具

    === 本项目的核心价值 ===
    这个工具解决了 AI 辅助开发中的关键问题:

    🎯 问题背景:
    - 在 Cursor 等环境中，每次 LLM 请求都计入月度限额
    - 模糊指令导致错误输出，需要多次澄清，浪费 API 调用
    - 缺乏实时交互能力，AI 只能基于猜测行动

    💡 解决方案:
    - 暂停并澄清: AI 可以暂停请求澄清，而不是盲目猜测
    - 节省资源: 避免基于错误理解生成无用代码
    - 提升效率: 一次正确胜过多次错误尝试
    - 增强控制: 用户始终掌控开发流程

    🚀 功能特性:
    - 智能提示词增强 (Gemini API 集成)
    - 灵活的会话控制机制
    - 预设选项快速选择
    - 上下文感知处理
    - 现代化用户界面

    Args:
        message: 向用户提出的具体问题或请求
        predefined_options: 预定义选项列表，提升交互效率
        context_info: 项目上下文信息，包括目标、进度、技术栈等

    Returns:
        List[TextContent]: 包含用户反馈和会话控制信息的文本内容列表
    """
    debug_log("开始处理用户反馈请求")
    debug_log(f"消息内容: {message[:100]}...")
    debug_log(f"预设选项: {predefined_options}")
    debug_log(f"上下文信息长度: {len(context_info) if context_info else 0}")

    predefined_options_list = predefined_options if isinstance(predefined_options, list) else None
    result = launch_feedback_ui(message, predefined_options_list, context_info)
    debug_log(f"UI 返回结果类型: {type(result)}")
    debug_log(f"UI 返回结果键: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

    # Create text content for the feedback
    text_feedback = result.get("interactive_feedback", "")
    session_control = result.get("session_control", "continue")
    images_data = result.get("images", [])

    # 构建完整的反馈文本，包含会话控制信息
    full_feedback_text = text_feedback
    if session_control:
        full_feedback_text += f"\n\n[会话控制: {session_control}]"

    debug_log(f"文本反馈长度: {len(full_feedback_text)}")
    debug_log(f"接收到图片数量: {len(images_data)}")

    # 处理图片数据
    images = process_images(images_data) if images_data else []
    debug_log(f"成功处理图片数量: {len(images)}")

    # 根据返回的实际内容组装结果
    debug_log("用户反馈处理完成")

    if full_feedback_text and images:
        # 有文本和图片
        result_tuple = (full_feedback_text, *images)
        debug_log(f"返回文本+图片: 1个文本 + {len(images)}张图片")
        return result_tuple
    elif full_feedback_text:
        # 只有文本
        debug_log("返回纯文本反馈")
        return (full_feedback_text,)
    elif images:
        # 只有图片
        debug_log(f"返回纯图片: {len(images)}张图片")
        return tuple(images)
    else:
        # 空反馈
        debug_log("返回空反馈")
        return ("",)

if __name__ == "__main__":
    mcp.run(transport="stdio")
