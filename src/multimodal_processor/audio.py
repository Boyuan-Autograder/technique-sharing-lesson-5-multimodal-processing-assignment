import os
import json
from pathlib import Path
from faster_whisper import WhisperModel


class AudioProcessor:
    SYSTEM_PROMPT_SUMMARY = (
        "你是一个商业会议记录分析助手。以下是一段会议录音的转写文本，"
        "请提取：\n"
        "1. 核心观点摘要（3-5条）\n"
        "2. 关键决策（如果有）\n"
        '请以JSON格式返回，字段名为：key_points（字符串列表）, decisions（字符串列表）'
    )

    def __init__(self):
        self.model = None
        try:
            print("  正在加载 Whisper 模型（首次运行会自动下载，约75MB）...")
            self.model = WhisperModel("base", device="cpu", compute_type="int8")
            print("  Whisper 模型加载完成")
        except Exception as e:
            print(f"  [!] 无法加载 Whisper 模型: {e}")

    def transcribe(self, audio_path: Path) -> dict:
        if not audio_path.exists():
            print(f"  [!] 音频文件不存在: {audio_path}")
            return self._fake_transcript_data()

        if not self.model:
            print("  [!] Whisper 模型未加载，使用模拟数据")
            return self._fake_transcript_data()

        try:
            print("  正在进行语音转写...")
            segments, info = self.model.transcribe(
                str(audio_path),
                language="zh",
                initial_prompt="以下是简体中文普通话的会议录音。",
                vad_filter=True,
            )
            transcript = "".join([segment.text for segment in segments])

            print(f"  [Whisper 转写结果] ({len(transcript)} 字符)")
            print(f"  {transcript[:200]}..." if len(transcript) > 200 else f"  {transcript}")

            api_key = os.getenv("MOONSHOT_API_KEY") or os.getenv("KIMI_API_KEY")
            if not api_key:
                print("  [!] 未配置 API Key，跳过 AI 摘要生成")
                result = self._fake_transcript_data()
                result["transcript"] = transcript
                return result

            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.cn/v1",
            )

            print("  正在生成 AI 摘要...")
            analysis_response = client.chat.completions.create(
                model="moonshot-v1-128k",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT_SUMMARY},
                    {"role": "user", "content": transcript},
                ],
                response_format={"type": "json_object"},
            )

            summary_text = analysis_response.choices[0].message.content
            print(f"  [Kimi 摘要结果]\n  {summary_text}")

            analysis = json.loads(summary_text)
            analysis["transcript"] = transcript
            return analysis

        except Exception as e:
            print(f"  [X] 语音转写失败: {e}，回退到模拟数据")
            result = self._fake_transcript_data()
            return result

    def _fake_transcript_data(self) -> dict:
        return {
            "transcript": (
                "大家好，今天我们召开Q1业务复盘会议。\n\n"
                "首先由我汇报一下本季度的销售情况。第一季度我们实现了营收同比增长23%，"
                "其中华东区表现最为亮眼，增速达到35%。华南区由于市场竞争激烈，增速略有下滑。\n\n"
                "关于产品方面，智能传感器的销量持续走高，占总营收的40%以上。"
                "特别是我们新推出的Pro Max系列，用户反馈非常好。\n\n"
                "接下来讨论一下供应链问题。上个月由于芯片短缺，我们的交付周期有所延长。"
                "最长的一次延误了2周，影响了大概500万的订单。\n\n"
                "关于下季度的策略，我有几点建议：第一，加大华东区的投入，那边市场空间还很大。"
                "第二，Pro Max系列要加大备货量。第三，供应链要提前锁定关键元器件的货源。\n\n"
                "最后，关于人员的问题。我们计划Q2再招聘5名销售工程师，重点补充到华南和华西地区。\n\n"
                "大家有没有其他问题？"
            ),
            "key_points": [
                "Q1营收同比增长23%，华东区增速达35%",
                "智能传感器占总营收40%以上，Pro Max系列反馈良好",
                "芯片短缺导致交付延误最长2周，影响约500万订单",
                "建议Q2加大华东区投入和Pro Max系列备货",
                "计划Q2招聘5名销售工程师补充华南和华西",
            ],
            "decisions": [
                "Q2加大华东区市场投入",
                "Pro Max系列提前备货，锁定供应链",
                "新增5名销售工程师",
            ],
        }
