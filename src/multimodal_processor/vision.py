import os
import json
import base64
from pathlib import Path
from openai import OpenAI


def get_api_key() -> str | None:
    return os.getenv("MOONSHOT_API_KEY") or os.getenv("KIMI_API_KEY")


def get_kimi_client() -> OpenAI | None:
    api_key = get_api_key()
    if api_key:
        return OpenAI(api_key=api_key, base_url="https://api.moonshot.cn/v1")
    return None


def encode_image_to_base64(image_path: Path) -> str:
    from PIL import Image
    import io
    img = Image.open(image_path)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    if img.width > 1024:
        ratio = 1024 / img.width
        img = img.resize((1024, int(img.height * ratio)), Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


class VisionProcessor:
    def __init__(self):
        self.client = get_kimi_client()

    def process_receipt(self, receipt_path: Path) -> dict:
        if not receipt_path.exists():
            print(f"  [!] 收据文件不存在: {receipt_path}")
            return self._fake_receipt_data()

        if not self.client:
            print("  [!] 未配置 API Key，使用模拟数据")
            return self._fake_receipt_data()

        try:
            base64_image = encode_image_to_base64(receipt_path)
            response = self.client.chat.completions.create(
                model="moonshot-v1-128k-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                            {
                                "type": "text",
                                "text": (
                                    "请仔细识别这张收据图片，提取以下信息并以JSON格式返回：\n"
                                    '{{"amount": "金额（含货币单位）", "date": "日期（YYYY-MM-DD格式）", "items": "商品名称及数量"}}'
                                ),
                            },
                        ],
                    }
                ],
                response_format={"type": "json_object"},
            )

            result_text = response.choices[0].message.content
            print(f"  [Kimi API Response]\n  {result_text}")

            result = json.loads(result_text)
            return result

        except Exception as e:
            print(f"  [X] 收据识别失败: {e}，回退到模拟数据")
            return self._fake_receipt_data()

    def process_formula(self, formula_path: Path) -> dict:
        if not formula_path.exists():
            print(f"  [!] 公式文件不存在: {formula_path}")
            return self._fake_formula_data()

        if not self.client:
            print("  [!] 未配置 API Key，使用模拟数据")
            return self._fake_formula_data()

        try:
            base64_image = encode_image_to_base64(formula_path)
            response = self.client.chat.completions.create(
                model="moonshot-v1-128k-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                            {
                                "type": "text",
                                "text": (
                                    "请分析这张图片中的手写公式，需要包含：\n"
                                    "1. 公式的LaTeX表示\n"
                                    "2. 公式中每个符号的含义\n"
                                    "3. 公式的推导逻辑和应用场景"
                                ),
                            },
                        ],
                    }
                ],
            )

            result_text = response.choices[0].message.content
            print(f"  [Kimi API Response]\n  {result_text[:200]}...")

            return {"formula": result_text}

        except Exception as e:
            print(f"  [X] 公式识别失败: {e}，回退到模拟数据")
            return self._fake_formula_data()

    def _fake_receipt_data(self) -> dict:
        return {
            "amount": "CNY 2,580.00",
            "date": "2024-03-15",
            "items": "Laser Range Finder Pro Max x 2, Mounting Bracket x 2",
        }

    def _fake_formula_data(self) -> dict:
        return {
            "formula": (
                "### 标准差公式\n\n"
                "$$\\sigma = \\sqrt{\\frac{\\sum (x_i - \\mu)^2}{n}}$$\n\n"
                "**符号说明：**\n"
                "- σ (sigma): 标准差\n"
                "- x_i: 第 i 个数据点\n"
                "- μ (mu): 数据均值\n"
                "- n: 数据点总数\n\n"
                "**推导逻辑：**\n"
                "1. 计算所有数据点的均值 μ = Σx_i / n\n"
                "2. 计算每个数据点与均值的偏差 (x_i - μ)\n"
                "3. 将偏差平方以消除正负号影响\n"
                "4. 求平方偏差的平均值（方差）\n"
                "5. 开平方得到标准差\n\n"
                "**应用场景：** 衡量销售数据的波动程度，辅助风险评估"
            ),
        }
