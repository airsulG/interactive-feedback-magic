# 🗣️ Interactive Feedback Magic
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-compatible-orange.svg)](https://modelcontextprotocol.io/)

基于 [Fábio Ferreira](https://x.com/fabiomlferreira) 和 [Pau Oliva](https://x.com/pof) 开发的优秀项目 [interactive-feedback-mcp](https://github.com/poliva/interactive-feedback-mcp)，在原有功能基础上做了一些微小的改进。这是一个 [MCP 服务器](https://modelcontextprotocol.io/)，为 AI 辅助开发工具（如 [Cursor](https://www.cursor.com)、[Cline](https://cline.bot) 和 [Windsurf](https://windsurf.com)）提供人机交互反馈功能。

## ✨ 主要特性

### 🎯 核心功能（继承自原项目）
- **🔄 交互式反馈**：通过图形界面与 AI 助手进行实时对话
- **📝 预设选项**：支持快速选择预定义的回复选项
- **🎨 用户界面**：基于 PySide6 的图形界面

### 改进
- **⚡ 提示词增强**：尝试集成 Google Gemini API，辅助优化提示词表达
- **🎮 会话控制**：灵活控制对话流程，选择继续或结束当前会话
- **🌍 上下文支持**：增加了项目上下文信息的传递功能
- **🔒 安全优化**：API 密钥通过环境变量管理

## 🎬 使用演示

![Interactive Feedback 演示](.github/example.png)

## 💡 项目价值（来自原作者的设计理念）

在 Cursor 等环境中，每次发送给 LLM 的提示都被视为独立请求，计入你的月度限额（如 500 次高级请求）。当你需要迭代模糊的指令或纠正误解的输出时，每次后续澄清都会触发新的完整请求，这变得非常低效。

**项目核心价值**：
- 🛑 **暂停并澄清**：模型可以暂停并请求澄清，而不是基于猜测完成请求
- 💰 **节省 API 调用**：避免浪费昂贵的 API 调用生成基于猜测的代码
- ✅ **减少错误**：在行动前澄清，意味着更少的错误代码和浪费的时间
- ⏱️ **更快的迭代**：快速确认胜过调试错误的猜测
- 🎮 **更好的协作**：将单向指令转变为对话，让你保持控制

## 📦 安装指南

### 前置要求
- **Python 3.11+**
- **[uv](https://github.com/astral-sh/uv)** 包管理器

### 安装 uv
```bash
# Windows
pip install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS
brew install uv
```

### 获取代码
```bash
git clone https://github.com/airsulG/interactive-feedback-magic.git
cd interactive-feedback-magic
```

## ⚙️ 配置指南

### 基础配置（无提示词增强）
在你的 `claude_desktop_config.json`（Claude Desktop）或 `mcp.json`（Cursor）中添加：
**记住将 `/path/to/interactive-feedback-magic` 路径更改为你在系统上克隆仓库的实际路径。**

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/interactive-feedback-magic",
        "run",
        "server.py"
      ],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

### 完整配置（包含提示词增强）
如果你想使用提示词增强功能，需要提供 Gemini API 密钥：

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/interactive-feedback-magic",
        "run",
        "server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "your-gemini-api-key-here"
      },
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

### 获取 Gemini API 密钥
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 使用 Google 账户登录
3. 创建新的 API 密钥
4. 将 `"your-gemini-api-key-here"` 替换为你的实际 API 密钥

## 🎯 使用方法

### AI 助手规则配置
在你的 AI 助手中添加以下自定义规则（Cursor 设置 > 规则 > 用户规则）：

## Interactive Feedback 使用规则

- 如果认为用户的指令、需求或目标不够清晰、存在歧义，或者缺少必要信息，你应该使用 `interactive_feedback` 工具向用户提问以澄清，而不是基于自己的猜测继续执行。

- 当有多个合理的执行路径或用户可能需要做选择时，你应该通过 `interactive_feedback` 的 `predefined_options` 参数提供预定义的选项，方便用户快速决策。

- 在任何会话输出的结尾，**始终**使用 `interactive_feedback` MCP 工具等待用户反馈；只有当用户没有提供反馈（空反馈）或者明确要求结束会话，才结束请求。

- **重要**：主动调用一次 `interactive_feedback` 来征求用户对整体结果的最终确认或反馈，通过 `interactive_feedback` 工具等待用户的最终确认或反馈，而不是直接结束会话。

- 当你调用 `interactive_feedback` 工具时，用户将通过工具输出中的 `session_control` 字段指定会话是应该继续还是终止：
  - 如果 `session_control` 的值为 `"continue"`，在处理完当前反馈并完成任何相关的子任务后，你应该再次调用 `interactive_feedback` 工具，以向用户询问进一步的澄清或下一步操作。你可以提示用户，例如"我已经根据你的反馈完成了 X。接下来你想做什么？"或者提出一个更具体的后续问题。
  - 如果 `session_control` 的值为 `"terminate"`，在处理完当前反馈并完成任何相关的子任务后，你应该认为本次特定的澄清循环交互已经完成，并继续最终完成用户的整体请求。除非后续出现全新的不明确之处，否则在此循环中不要再次调用 `interactive_feedback`，然后给予用户鼓励并自然地结束会话。

## 🔧 开发指南

### 项目结构
```
interactive-feedback-magic/
├── server.py              # MCP 服务器主文件
├── feedback_ui.py          # 图形用户界面
├── prompt_enhancer.py      # 提示词增强服务
├── ui_styles.py           # UI 样式定义
├── session_control.py     # 会话控制组件
├── prompt_enhancement_widget.py # 提示词增强组件
├── README_CN.md           # 中文文档
├── CHANGES.md             # 变更说明
└── assets/                # 资源文件
    └── magic.svg          # 图标资源
```

### 本地开发
```bash
# 安装依赖
uv sync

# 运行服务器
python server.py

# 测试 UI
python feedback_ui.py --prompt "测试消息"
```

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 开源协议

本项目基于 [Apache 2.0 协议](LICENSE) 开源。

## 🙏 致谢

特别感谢原作者的优秀工作：
- **原始项目**：[interactive-feedback-mcp](https://github.com/poliva/interactive-feedback-mcp) by [Fábio Ferreira](https://x.com/fabiomlferreira) 和 [Pau Oliva](https://x.com/pof)
- **灵感来源**：Tommy Tong 的 [interactive-mcp](https://github.com/ttommyth/interactive-mcp)
- **技术支持**：[Model Context Protocol](https://modelcontextprotocol.io/) 社区

本项目只是在原有优秀基础上做了一些微小的改进，所有核心功能和设计理念都来自原作者的贡献。

## 📞 支持与反馈

如果你遇到问题或有建议，请：
- 提交 [Issue](https://github.com/airsulG/interactive-feedback-magic/issues)
- 参与 [Discussions](https://github.com/airsulG/interactive-feedback-magic/discussions)
- 查看原项目 [interactive-feedback-mcp](https://github.com/poliva/interactive-feedback-mcp) 获取更多文档

---