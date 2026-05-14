# technique-sharing-lesson-5-multimodal-processing-assignment

## 课后练习：多模态处理技术

本作业模板用于练习综合运用多模态处理、结构化数据解析与语音转写技术。

---

## 任务概述

对一份混合格式的文件包进行全量解析，整合分散的信息，输出一份逻辑清晰、要素完整的"季度业务简报"。

---

## 输入文件清单

| 文件 | 类型 | 处理方式 |
|------|------|----------|
| `data/receipt.png` | 图片型收据 | Base64编码 → Kimi视觉识别API |
| `data/sales.csv` | 结构化数据 | Pandas读取分析 → Markdown表格 |
| `data/formula.png` | 手写公式 | Base64编码 → Kimi视觉API提取 |
| `data/summary.mp3` | 录音文件 | Faster-Whisper本地语音转写 |

---

## 输出标准

你的程序最终需要生成一份 `output/report.md`，包含以下四个部分：

### 1. 财务摘要
- 收据金额
- 业务发生日期

### 2. 经营亮点
- 本季度销售额 Top1 的产品

### 3. 技术细节
- 手写公式的含义与推导逻辑

### 4. 决策录音
- 完整转写文本
- 核心观点摘要

---

## 环境配置

### 前置要求
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (包管理器)

### 安装依赖

```bash
uv sync
```

### 环境变量

创建 `.env` 文件，配置你的API密钥：

```bash
# Moonshot Kimi API (用于视觉识别)
MOONSHOT_API_KEY=your_kimi_api_key_here
```

获取API Key: https://platform.moonshot.cn/

---

## 项目结构

```
.
├── README.md
├── plan.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── data/
│   ├── receipt.png          # 输入：收据图片
│   ├── sales.csv            # 输入：销售数据
│   ├── formula.png          # 输入：手写公式
│   └── summary.mp3          # 输入：语音录音
├── src/
│   └── multimodal_processor/
│       ├── __init__.py
│       ├── main.py          # 主程序入口
│       ├── vision.py        # 视觉识别模块 (Kimi)
│       ├── audio.py         # 语音转写模块 (Faster-Whisper)
│       ├── csv_parser.py    # CSV解析模块
│       └── report.py        # 报告生成模块
├── output/
│   └── report.md            # 输出：生成的简报
└── tests/
    └── test_processor.py   # 单元测试
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone <repository-url>
cd technique-sharing-lesson-5-multimodal-processing-assignment
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 Moonshot API Key
```

### 4. 准备数据

将以下文件放入 `data/` 目录：
- `receipt.png` - 收据图片
- `sales.csv` - 销售数据CSV
- `formula.png` - 手写公式
- `summary.mp3` - 语音录音

### 5. 运行程序

```bash
uv run python -m multimodal_processor.main
```

### 6. 查看输出

生成的报告位于 `output/report.md`

---

## API说明

本项目使用以下服务：

### Moonshot Kimi Vision (视觉识别)
- 用途：图像内容识别（收据、公式）
- 文档：https://platform.moonshot.cn/docs/api/chat
- 模型：`moonshot-v1-128k-vision-preview`

### Faster-Whisper (本地语音转写)
- 用途：音频转文字（完全本地，无需API）
- 文档：https://github.com/guillaayak/faster-whisper
- 模型：Whisper base（首次运行自动下载）

---

## 数据说明

为方便测试，本仓库的 `data/` 目录包含**伪造的示例数据**（由你生成）。

---

## 评分标准

| 项目 | 分数 | 要求 |
|------|------|------|
| 财务摘要 | 25% | 准确提取收据金额和日期 |
| 经营亮点 | 25% | 正确识别销售额Top1产品 |
| 技术细节 | 25% | 正确解析公式含义 |
| 决策录音 | 25% | 完整转写并提取核心观点 |

---

## 常见问题

### Q: 视觉API调用失败怎么办？
A: 检查 `.env` 中的 `MOONSHOT_API_KEY` 是否正确配置。

### Q: Whisper模型下载慢？
A: 首次运行会自动下载模型（约75MB），可使用VPN加速。

### Q: CSV编码问题？
A: 确保CSV文件使用UTF-8编码。

---

## 许可

本项目仅用于教学目的。