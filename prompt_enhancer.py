# Prompt Enhancement Service - 智能提示词增强服务
#
# === 核心改进功能 ===
# 本模块是项目的重要创新之一，提供智能提示词优化能力
#
# 🎯 功能价值:
# - 将用户的简单想法转化为结构化、可执行的任务描述
# - 自动补充技术细节和实现步骤
# - 提供分阶段执行计划，提升开发效率
# - 支持上下文感知，结合项目背景优化建议
#
# 🔒 安全性改进:
# - 完全移除硬编码 API 密钥
# - 通过环境变量安全管理敏感信息
# - 完善的错误处理和用户友好的提示
#
# ⚡ 技术特性:
# - 支持流式和非流式两种处理模式
# - 集成 Google Gemini 2.5 Flash 最新模型
# - 智能上下文处理和模板化输出
# - 异步处理支持，提升用户体验

import os
import logging

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === 智能提示词增强模板 ===
# 这是本项目的核心创新之一，通过精心设计的提示词模板
# 将用户的模糊想法转化为结构化、可执行的开发任务
ENHANCEMENT_SYSTEM_PROMPT_TEMPLATE = """# 任务
将用户的初步想法转化为清晰、结构化、可执行的任务描述。

# 输出格式要求
请严格按照以下格式输出，确保结构清晰、分阶段执行：

## 核心目标
用1-2句话概括用户想要达成的最终成果和主要价值。

## 具体要求如下：

**第一阶段：[阶段名称]**
1. [具体行动项1]
2. [具体行动项2]
3. [具体行动项3]

**第二阶段：[阶段名称]**
4. [具体行动项4]
5. [具体行动项5]
6. [具体行动项6]

**第三阶段：[阶段名称]**（如需要）
7. [具体行动项7]
8. [具体行动项8]

**技术要求：**
- [技术要求1]
- [技术要求2]
- [技术要求3]

**预期成果：**
[详细描述最终交付物和验收标准]

# 优化原则
1. **分阶段执行**：将任务分解为2-3个逻辑清晰的执行阶段
2. **具体行动项**：每个步骤都要具体、可操作，避免模糊表述
3. **技术细节**：补充必要的技术要求、约束条件和实现细节
4. **实际价值**：确保每个步骤都指向明确的价值产出

# 请基于以上格式和原则，开始转化用户的表达。
"""


def enhance_prompt_with_gemini(user_text: str, context_info: str = "") -> str:
    """
    智能提示词增强函数 - 核心功能实现

    === 功能亮点 ===
    这是本项目的重要创新功能，解决了以下问题:

    🎯 解决的问题:
    - 用户提供的需求往往模糊不清
    - 缺乏技术细节和实现步骤
    - AI 难以理解真正的意图和目标

    💡 提供的价值:
    - 自动结构化用户想法
    - 补充技术要求和实现细节
    - 分阶段规划执行步骤
    - 结合项目上下文提供精准建议

    🔒 安全性改进:
    - 移除硬编码 API 密钥，通过环境变量管理
    - 完善的错误处理和用户友好提示
    - 输入验证和异常安全处理

    Args:
        user_text: 用户输入的原始文本或想法
        context_info: 项目上下文信息，帮助 AI 更好理解需求

    Returns:
        str: 结构化增强后的提示词，或错误信息

    Example:
        输入: "我想优化这个函数"
        输出: 详细的优化计划，包括具体步骤、技术要求和预期成果
    """
    if not genai or not types:
        return "错误：Google Gen AI SDK 未正确安装。请运行 'pip install google-genai' 安装依赖。"

    # 检查 API 密钥 - 仅使用环境变量
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "错误：未找到 GEMINI_API_KEY 环境变量。请在 MCP 配置中设置该环境变量。"

    if not user_text.strip():
        return "错误：请输入需要增强的文本内容。"
    
    try:
        # 创建客户端
        client = genai.Client(api_key=api_key)

        # 构建请求内容 - 包含用户文本和上下文信息
        user_content = user_text
        if context_info and context_info.strip():
            user_content = f"**项目上下文信息：**\n{context_info}\n\n**用户需求：**\n{user_text}"

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_content)]
            )
        ]

        # 配置生成参数 - 将增强模板设置为系统指令
        config = types.GenerateContentConfig(
            system_instruction=[
                types.Part.from_text(text=ENHANCEMENT_SYSTEM_PROMPT_TEMPLATE)
            ],
            response_mime_type="text/plain",
            temperature=0.7
        )

        # 调用 API
        logger.info("正在调用 Gemini API 进行提示词增强...")
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",  # 使用最新的预览模型
            contents=contents,
            config=config
        )

        # 获取响应文本
        enhanced_text = response.text
        if enhanced_text:
            logger.info("提示词增强完成")
            return enhanced_text.strip()
        else:
            return "错误：API 返回了空响应。请检查您的输入或稍后重试。"

    except Exception as e:
        error_msg = f"错误：调用 Gemini API 时发生异常：{str(e)}"
        logger.error(error_msg)
        return error_msg


def enhance_prompt_with_gemini_stream(user_text: str) -> str:
    """
    使用流式方式调用 Gemini API 增强用户提示词

    Args:
        user_text: 用户输入的原始文本

    Returns:
        增强后的文本，如果出错则返回错误信息
    """
    if not genai or not types:
        return "错误：Google Gen AI SDK 未正确安装。请运行 'pip install google-genai' 安装依赖。"

    # 检查 API 密钥 - 仅使用环境变量
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "错误：未找到 GEMINI_API_KEY 环境变量。请在 MCP 配置中设置该环境变量。"

    if not user_text.strip():
        return "错误：请输入需要增强的文本内容。"
    
    try:
        # 创建客户端
        client = genai.Client(api_key=api_key)

        # 构建请求内容 - 直接发送用户文本
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_text)]
            )
        ]

        # 配置生成参数 - 将增强模板设置为系统指令
        config = types.GenerateContentConfig(
            system_instruction=[
                types.Part.from_text(text=ENHANCEMENT_SYSTEM_PROMPT_TEMPLATE)
            ],
            response_mime_type="text/plain",
            temperature=0.7
        )

        # 调用流式 API
        logger.info("正在调用 Gemini API 进行提示词增强（流式）...")
        enhanced_text_parts = []

        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash-preview-05-20",
            contents=contents,
            config=config
        ):
            if chunk.text:
                enhanced_text_parts.append(chunk.text)

        # 组合所有文本块
        enhanced_text = "".join(enhanced_text_parts)
        if enhanced_text:
            logger.info("提示词增强完成")
            return enhanced_text.strip()
        else:
            return "错误：API 返回了空响应。请检查您的输入或稍后重试。"

    except Exception as e:
        error_msg = f"错误：调用 Gemini API 时发生异常：{str(e)}"
        logger.error(error_msg)
        return error_msg


def enhance_prompt_with_gemini_stream_generator(user_text: str, context_info: str = ""):
    """
    使用流式方式调用 Gemini API 增强用户提示词，返回生成器

    Args:
        user_text: 用户输入的原始文本
        context_info: 上下文信息（可选）

    Yields:
        str: 增强文本的块
    """
    if not genai or not types:
        yield "错误：Google Gen AI SDK 未正确安装。请运行 'pip install google-genai' 安装依赖。"
        return

    # 检查 API 密钥 - 仅使用环境变量
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        yield "错误：未找到 GEMINI_API_KEY 环境变量。请在 MCP 配置中设置该环境变量。"
        return

    if not user_text.strip():
        yield "错误：请输入需要增强的文本内容。"
        return

    try:
        # 创建客户端
        client = genai.Client(api_key=api_key)

        # 构建请求内容 - 包含用户文本和上下文信息
        user_content = user_text
        if context_info and context_info.strip():
            user_content = f"**项目上下文信息：**\n{context_info}\n\n**用户需求：**\n{user_text}"

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_content)]
            )
        ]

        # 配置生成参数 - 将增强模板设置为系统指令
        config = types.GenerateContentConfig(
            system_instruction=[
                types.Part.from_text(text=ENHANCEMENT_SYSTEM_PROMPT_TEMPLATE)
            ],
            response_mime_type="text/plain",
            temperature=0.7
        )

        # 调用流式 API
        logger.info("正在调用 Gemini API 进行提示词增强（流式生成器）...")

        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash-preview-05-20",
            contents=contents,
            config=config
        ):
            if chunk.text:
                yield chunk.text

        logger.info("提示词增强完成")

    except Exception as e:
        error_msg = f"错误：调用 Gemini API 时发生异常：{str(e)}"
        logger.error(error_msg)
        yield error_msg
