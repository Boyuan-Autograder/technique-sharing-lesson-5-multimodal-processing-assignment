# 多模态混合文件解析 — 课后练习

> technique-sharing-lesson-5-multimodal-processing-assignment

综合运用**视觉识别**、**结构化数据解析**与**语音转写**技术，将一个包含多种格式的混合文件包全量解析为一份逻辑清晰的"季度业务简报"。

---

## 快速开始

### 0. 前置要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)（Python 包管理器）

### 1. 克隆并进入项目

```bash
git clone <repo-url>
cd technique-sharing-lesson-5-multimodal-processing-assignment
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 Kimi API Key：

```
MOONSHOT_API_KEY=sk-your-api-key-here
```

> 获取 Key：https://platform.moonshot.cn/ — 新用户有免费额度。

### 4. 准备输入文件

将以下 4 个文件放入 `data/` 目录：

| 文件 | 类型 | 说明 |
|------|------|------|
| `data/receipt.png` | 收据图片 | 购物小票/发票照片 |
| `data/sales.csv` | 结构化表格 | 季度销售记录 |
| `data/formula.png` | 手写公式 | 手写数学公式图片 |
| `data/summary.mp3` | 录音文件 | 会议录音（支持中文） |

> 仓库自带示例数据（`data/` 目录下），可开箱即用。

### 5. 运行

```bash
uv run -m multimodal_processor.main
```

程序会依次处理 4 个文件，并在终端打印处理进度和大模型响应结果。

### 6. 查看输出

生成的报告位于 `output/report.md`，包含四个部分：

1. **财务摘要** — 收据金额与日期
2. **经营亮点** — 销售额 Top1 产品与排行
3. **技术细节** — 手写公式的含义与推导
4. **决策录音** — 完整转写文本与核心观点摘要

---

## 项目结构

```
.
├── README.md
├── plan.md                          # 任务说明（给学生）
├── pyproject.toml                   # 项目配置（uv + hatchling）
├── .env.example                     # 环境变量模板
├── .gitignore
├── data/                            # 输入文件目录
│   ├── receipt.png                  # 收据图片
│   ├── sales.csv                    # 销售数据
│   ├── formula.png                  # 手写公式
│   └── summary.mp3                  # 会议录音
├── src/multimodal_processor/        # 源代码
│   ├── __init__.py
│   ├── main.py                      # 主程序入口
│   ├── vision.py                    # 视觉识别（Kimi）
│   ├── audio.py                     # 语音转写（Faster-Whisper）
│   ├── csv_parser.py                # CSV 解析（Pandas）
│   └── report.py                    # 报告生成
├── output/                          # 输出目录
│   └── report.md                    # 生成的简报
└── tests/
    └── test_processor.py            # 单元测试
```

---

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 视觉识别 | Moonshot Kimi Vision API | 识别收据图片和手写公式 |
| 语音转写 | Faster-Whisper (本地) | 将 MP3 录音转为文字，无需 API |
| 文本摘要 | Moonshot Kimi Chat API | 从转写文本中提取核心观点 |
| 数据分析 | Pandas | 读取 CSV、汇总销售额、排行 |
| 报告生成 | Python 字符串模板 | 输出 Markdown 格式报告 |

### 使用的 API

- **Kimi Vision API** (`moonshot-v1-128k-vision-preview`) — 图像内容识别
- **Kimi Chat API** (`moonshot-v1-128k`) — 文本摘要与结构化提取
- **Faster-Whisper** (`base` 模型) — 本地语音转写，首次运行自动下载约 75MB

---

## 常见问题

### Q: 运行时报 "未配置 API Key，使用模拟数据"？

A: 检查 `.env` 中是否正确设置了 `MOONSHOT_API_KEY`。需要去 https://platform.moonshot.cn 申请。

### Q: Whisper 模型下载慢？

A: 首次运行会自动下载约 75MB 的模型文件。如网络受限，可配置代理后重试。

### Q: 收据/公式识别失败？

A: 确保图片文件存在且格式为 PNG。程序会自动把大图缩放到 1024px 宽度以节省 Token。

### Q: CSV 读取报错？

A: 确保 CSV 使用 UTF-8 编码，且包含 `product` 和 `sales` 两列。

### Q: 没有 API Key 能运行吗？

A: 可以。程序会使用内置的模拟数据生成报告，只是不会调用真实的视觉 API。

---

## 运行测试

```bash
uv run pytest tests/ -v
```

---

## 评分标准

| 项目 | 权重 | 要求 |
|------|------|------|
| 财务摘要 | 25% | 准确提取收据金额和日期 |
| 经营亮点 | 25% | 正确识别销售额 Top1 产品 |
| 技术细节 | 25% | 正确解析公式含义 |
| 决策录音 | 25% | 完整转写并提取核心观点 |

---

## License

仅用于教学目的。
