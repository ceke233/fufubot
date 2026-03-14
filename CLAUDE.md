# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

nanobot 是一个超轻量级的个人 AI 助手框架，支持多渠道接入（Telegram、Feishu、DingTalk、Discord、WhatsApp 等）、工具调用、定时任务、MCP 集成等功能。

## 项目结构

```
fufubot/
├── nanobot/                    # 核心代码
│   ├── agent/                  # Agent 核心
│   │   ├── loop.py            # AgentLoop 主循环引擎
│   │   ├── context.py         # ContextBuilder 上下文构建
│   │   ├── memory.py          # MemoryConsolidator 记忆整合
│   │   ├── skills.py          # 技能加载和管理
│   │   ├── subagent.py        # SubagentManager 子代理管理
│   │   └── tools/             # 工具系统
│   │       ├── base.py        # Tool 抽象基类
│   │       ├── registry.py    # ToolRegistry 工具注册表
│   │       ├── shell.py       # ExecTool 命令执行
│   │       ├── filesystem.py  # 文件操作工具
│   │       ├── web.py         # WebSearch/WebFetch
│   │       ├── mcp.py         # MCP 工具封装
│   │       ├── message.py     # MessageTool 消息发送
│   │       ├── cron.py        # CronTool 定时任务
│   │       ├── spawn.py       # SpawnTool 子进程
│   │       └── voice.py       # VoiceTool 语音处理
│   │
│   ├── bus/                   # 消息总线
│   │   ├── queue.py          # MessageBus 消息队列
│   │   └── events.py         # InboundMessage/OutboundMessage
│   │
│   ├── channels/              # 渠道接入
│   │   ├── base.py           # BaseChannel 抽象基类
│   │   ├── registry.py       # 渠道注册表
│   │   ├── manager.py        # ChannelManager 管理器
│   │   ├── telegram.py       # Telegram 渠道
│   │   ├── feishu.py         # 飞书渠道
│   │   ├── dingtalk.py       # 钉钉渠道
│   │   ├── discord.py        # Discord 渠道
│   │   ├── whatsapp.py       # WhatsApp 渠道
│   │   ├── qq.py             # QQ 渠道
│   │   ├── napcat.py         # NapCat 渠道
│   │   ├── slack.py          # Slack 渠道
│   │   ├── wecom.py          # 企业微信渠道
│   │   ├── matrix.py         # Matrix 渠道
│   │   ├── email.py          # Email 渠道
│   │   └── mochat.py         # MoChat 渠道
│   │
│   ├── providers/             # LLM Provider
│   │   └── base.py           # LLMProvider 抽象基类（基于 litellm）
│   │
│   ├── session/               # 会话管理
│   │   └── manager.py        # SessionManager/Session
│   │
│   ├── config/                # 配置系统
│   │   ├── schema.py         # Config schema (Pydantic)
│   │   ├── loader.py         # 配置加载器
│   │   └── paths.py          # 路径管理
│   │
│   ├── cron/                  # 定时任务
│   │   ├── service.py        # CronService 调度器
│   │   └── types.py          # 定时任务类型定义
│   │
│   ├── heartbeat/             # 心跳唤醒
│   │   └── service.py        # HeartbeatService
│   │
│   ├── voice/                 # 语音处理
│   │   ├── tts/              # 语音合成
│   │   └── asr/              # 语音识别
│   │
│   ├── skills/                # 内置技能
│   │   ├── clawhub/          # ClawHub 集成
│   │   ├── cron/             # 定时任务技能
│   │   ├── github/           # GitHub 集成
│   │   ├── memory/           # 记忆管理技能
│   │   ├── skill-creator/    # 技能创建器
│   │   ├── summarize/        # 摘要技能
│   │   ├── tmux/             # Tmux 集成
│   │   └── weather/          # 天气查询
│   │
│   ├── templates/             # 模板文件
│   │   └── memory/           # 记忆模板
│   │
│   ├── utils/                 # 工具函数
│   │
│   └── cli/                   # CLI 命令
│       └── commands.py       # Typer CLI 入口
│
├── bridge/                    # WhatsApp Bridge (TypeScript)
│   └── src/                  # Bridge 源码
│
├── tests/                     # 测试文件
│   ├── test_commands.py      # CLI 测试
│   ├── test_*.py             # 各模块测试
│   └── send_test_message.py  # 消息测试工具
│
├── docs/                      # 文档
├── case/                      # 案例
├── pyproject.toml            # 项目配置
├── uv.lock                   # uv 依赖锁定
└── README.md                 # 项目说明
```

## 核心架构

### 1. Agent Loop (核心引擎)
- `nanobot/agent/loop.py` - AgentLoop 是核心处理引擎
- 处理流程：接收消息 → 构建上下文 → 调用 LLM → 执行工具 → 返回响应
- 最大迭代次数：40 次（`max_iterations`）
- 上下文窗口：65,536 tokens

### 2. 消息总线架构
- `nanobot/bus/queue.py` - MessageBus 消息队列
- `nanobot/bus/events.py` - InboundMessage/OutboundMessage 事件
- 所有渠道通过消息总线与 Agent 解耦

### 3. 渠道系统 (Channels)
- `nanobot/channels/base.py` - BaseChannel 抽象基类
- `nanobot/channels/registry.py` - 渠道注册表
- `nanobot/channels/manager.py` - ChannelManager 管理器
- 支持的渠道：telegram, feishu, dingtalk, discord, whatsapp, qq, slack, wecom, matrix, email, napcat, mochat

### 4. LLM Provider
- `nanobot/providers/` - 基于 litellm 的统一 LLM 接口
- 支持 OpenAI、Azure OpenAI、Anthropic、本地模型等

### 5. 工具系统 (Tools)
- `nanobot/agent/tools/registry.py` - ToolRegistry 工具注册表
- 内置工具：shell (ExecTool), filesystem (Read/Write/Edit/ListDir), web (Search/Fetch), message, cron, spawn, voice
- MCP 工具：`nanobot/agent/tools/mcp.py` - 动态加载 MCP 服务器工具

### 6. 会话管理
- `nanobot/session/manager.py` - SessionManager 会话管理器
- 每个会话绑定到特定用户和渠道
- 支持多用户隔离

### 7. 记忆系统
- `nanobot/agent/memory.py` - MemoryConsolidator 记忆整合器
- 支持短期记忆、长期记忆、情景记忆

## 常用开发命令

### 环境设置
```bash
# 激活 uv 虚拟环境
source .venv/bin/activate

# 安装依赖
uv pip install -e ".[dev]"
```

### 运行和测试
```bash
# 运行 nanobot CLI
nanobot --help
nanobot run --config config.json

# 运行测试
pytest
pytest tests/test_commands.py  # 单个测试文件
pytest -m "not integration"     # 跳过集成测试
```

### 代码质量
```bash
# 代码格式化和检查
ruff check .
ruff format .

# 统计核心代码行数
bash core_agent_lines.sh
```

### 配置文件
- 配置文件位置：`~/.nanobot/config.json` 或通过 `--config` 指定
- 配置 schema：`nanobot/config/schema.py`
- 模板文件：`nanobot/templates/`

## 关键设计模式

### 1. 注册表模式
所有可扩展组件（渠道、工具、Provider）都使用注册表模式：
```python
from nanobot.channels.registry import channel_registry

@channel_registry.register("my_channel")
class MyChannel(BaseChannel):
    ...
```

### 2. 异步优先
整个项目基于 asyncio，所有 I/O 操作都是异步的。

### 3. 配置驱动
使用 Pydantic 进行配置验证和类型检查（`config/schema.py`）。

### 4. 消息总线解耦
渠道和 Agent 通过消息总线通信，实现松耦合。

## 测试注意事项

- 集成测试需要真实的 API 密钥，使用 `@pytest.mark.integration` 标记
- 测试文件命名：`test_*.py`
- 异步测试自动启用（`asyncio_mode = "auto"`）

## 项目依赖

- **核心**：typer (CLI), litellm (LLM), pydantic (配置), loguru (日志)
- **渠道**：python-telegram-bot, lark-oapi, dingtalk-stream, discord.py, slack-sdk 等
- **工具**：httpx (HTTP), ddgs (搜索), croniter (定时), mcp (MCP 协议)
- **开发**：pytest, pytest-asyncio, ruff

## 代码风格

- 行长度：100 字符
- Python 版本：≥3.11
- 使用 ruff 进行 linting（规则：E, F, I, N, W，忽略 E501）
- 注释语言：与现有代码保持一致（中英文混合）
