# Requirement Clarification Service - 智能需求澄清服务
#
# === 核心改进功能 ===
# 本模块是项目的重要创新之一，提供智能需求澄清能力
#
# 🎯 功能价值:
# - 将用户的模糊想法转化为清晰、具体的需求列表
# - 识别并澄清模糊概念和主观词汇
# - 明确功能边界、性能指标和验收标准
# - 专注于"做什么"而非"怎么做"，避免过早的方案设计
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

# === 需求澄清模板 ===
# 这是本项目的核心创新之一，专注于将用户的模糊想法转化为清晰的需求列表
# 不进行方案设计，只进行需求澄清和具体化
REQUIREMENT_CLARIFICATION_TEMPLATE = """# 角色
你是一个顶级的AI需求分析专家，极其擅长识别用户表达中的模糊、不确切之处。

# 任务
你的唯一任务是对用户提供的"原始意图"进行需求澄清和具体化，而不是进行方案设计或提供解决方案。你需要将模糊的描述转化为一系列清晰、可衡量、可执行的具体需求点。

# 输出规则
1. **禁止方案设计**：不要提出实现方式、技术选型或具体的执行步骤。只关注"做什么"，不关注"怎么做"。
2. **禁止引导语**：直接输出最终澄清内容，不要添加任何如"好的，这是为您澄清后的需求："之类的开场白或解释。
3. **严格遵循格式**：输出必须严格按照以下结构：
   * 第一行为"**明确核心任务：**"后跟一句话总结的核心目标。
   * 其后为"**澄清需求列表：**"标题，下面是具体的澄清需求点列表。

# 澄清重点
- 识别模糊概念并直接提供具体定义建议（如"好用"、"快速"、"准确"等主观词汇）
- 明确功能边界和范围限制的具体选项
- 量化性能指标和评估标准的具体数值建议
- 确定输入输出格式和数据类型的具体选项
- 澄清用户群体和使用场景的具体描述
- 识别潜在的约束条件和限制因素的具体内容
- 明确验收标准和成功指标的具体标准

# 重要提醒
你不是在让用户填空或思考，而是直接为用户补全和澄清需求。每个澄清点都应该包含具体的建议选项和示例，让用户可以直接选择或参考。

# 输出示例
以下是一个标准的需求澄清示例：

**输入：** "我想要一个能总结长篇文章的工具，要做得好用、快速、准确。"

**输出：**
开发一个能够输入长篇文章并生成其核心内容摘要的AI工具。
- 定义"长篇文章"的具体标准（建议选项：500-2000字短文、2000-5000字中文、5000字以上长文；支持格式：纯文本、PDF、Word文档、网页链接）
- 明确摘要的输出格式（建议选项：一段式摘要100-200字、关键点列表式摘要3-5条、可自定义长度的摘要）
- 阐述"好用"的用户体验标准（建议选项：简洁的Web界面、支持API调用、一键完成操作、批量处理功能；目标用户：学生、研究人员、内容创作者）
- 量化"快速"的性能指标（建议标准：5000字文章在3秒内完成、支持并发处理、响应时间不超过5秒）
- 设定"准确"的评估标准（建议标准：保留原文关键信息95%以上、包含主要人名地名、保持原文逻辑结构、支持多语言准确性验证）
- 确定支持的输入语言范围（建议选项：仅中文、仅英文、中英双语、多语言支持）
- 界定工具的核心边界（建议功能：纯摘要功能、摘要+关键词提取、摘要+问答、摘要+情感分析）

# 请开始进行需求澄清：
"""


def enhance_prompt_with_gemini(user_text: str, context_info: str = "") -> str:
    """
    智能需求澄清函数 - 核心功能实现

    === 功能亮点 ===
    这是本项目的重要创新功能，专注于需求澄清而非方案设计:

    🎯 解决的问题:
    - 用户提供的需求往往模糊不清
    - 缺乏明确的功能边界和验收标准
    - AI 难以理解真正的意图和目标

    💡 提供的价值:
    - 识别并澄清模糊概念和主观词汇
    - 明确功能边界和范围限制
    - 量化性能指标和评估标准
    - 确定输入输出格式和数据类型
    - 澄清用户群体和使用场景

    🔒 安全性改进:
    - 移除硬编码 API 密钥，通过环境变量管理
    - 完善的错误处理和用户友好提示
    - 输入验证和异常安全处理

    Args:
        user_text: 用户输入的原始文本或想法
        context_info: 项目上下文信息，帮助 AI 更好理解需求

    Returns:
        str: 澄清后的需求列表，或错误信息

    Example:
        输入: "我想要一个能总结长篇文章的工具，要做得好用、快速、准确"
        输出: 明确核心任务和详细的需求澄清列表，包括对"好用"、"快速"、"准确"等模糊概念的具体化要求
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

        # 配置生成参数 - 将需求澄清模板设置为系统指令
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,  # 禁用思考，提升反应速度
            ),
            system_instruction=[
                types.Part.from_text(text=REQUIREMENT_CLARIFICATION_TEMPLATE)
            ],
            response_mime_type="text/plain",
            temperature=0.7
        )

        # 调用 API
        logger.info("正在调用 Gemini API 进行需求澄清...")
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",  # 使用最新的预览模型
            contents=contents,
            config=config
        )

        # 获取响应文本
        clarified_text = response.text
        if clarified_text:
            logger.info("需求澄清完成")
            return clarified_text.strip()
        else:
            return "错误：API 返回了空响应。请检查您的输入或稍后重试。"

    except Exception as e:
        error_msg = f"错误：调用 Gemini API 时发生异常：{str(e)}"
        logger.error(error_msg)
        return error_msg


def enhance_prompt_with_gemini_stream(user_text: str) -> str:
    """
    使用流式方式调用 Gemini API 进行需求澄清

    Args:
        user_text: 用户输入的原始文本

    Returns:
        澄清后的需求列表，如果出错则返回错误信息
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

        # 配置生成参数 - 将需求澄清模板设置为系统指令
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,  # 禁用思考，提升反应速度
            ),
            system_instruction=[
                types.Part.from_text(text=REQUIREMENT_CLARIFICATION_TEMPLATE)
            ],
            response_mime_type="text/plain",
            temperature=0.7
        )

        # 调用流式 API
        logger.info("正在调用 Gemini API 进行需求澄清（流式）...")
        clarified_text_parts = []

        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash-preview-05-20",
            contents=contents,
            config=config
        ):
            if chunk.text:
                clarified_text_parts.append(chunk.text)

        # 组合所有文本块
        clarified_text = "".join(clarified_text_parts)
        if clarified_text:
            logger.info("需求澄清完成")
            return clarified_text.strip()
        else:
            return "错误：API 返回了空响应。请检查您的输入或稍后重试。"

    except Exception as e:
        error_msg = f"错误：调用 Gemini API 时发生异常：{str(e)}"
        logger.error(error_msg)
        return error_msg


def enhance_prompt_with_gemini_stream_generator(user_text: str, context_info: str = ""):
    """
    使用流式方式调用 Gemini API 进行需求澄清，返回生成器

    Args:
        user_text: 用户输入的原始文本
        context_info: 上下文信息（可选）

    Yields:
        str: 澄清需求的文本块
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

        # 配置生成参数 - 将需求澄清模板设置为系统指令
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,  # 禁用思考，提升反应速度
            ),
            system_instruction=[
                types.Part.from_text(text=REQUIREMENT_CLARIFICATION_TEMPLATE)
            ],
            response_mime_type="text/plain",
            temperature=0.7
        )

        # 调用流式 API
        logger.info("正在调用 Gemini API 进行需求澄清（流式生成器）...")

        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash-preview-05-20",
            contents=contents,
            config=config
        ):
            if chunk.text:
                yield chunk.text

        logger.info("需求澄清完成")

    except Exception as e:
        error_msg = f"错误：调用 Gemini API 时发生异常：{str(e)}"
        logger.error(error_msg)
        yield error_msg
