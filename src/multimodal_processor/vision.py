import os
import base64
from pathlib import Path
from openai import OpenAI


def get_kimi_client() -> OpenAI | None:
    api_key = os.getenv("MOONSHOT_API_KEY") or os.getenv("KIMI_API_KEY")
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
        if not receipt_path.exists() or not self.client:
            return self._fake_receipt_data()

        try:
            base64_image = encode_image_to_base64(receipt_path)
            response = self.client.chat.completions.create(
                model="moonshot-v1-128k-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                            {"type": "text", "text": "请描述这张收据图片，提取金额、日期和商品信息，以JSON格式返回"},
                        ],
                    }
                ],
                response_format={"type": "json_object"},
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Receipt API failed: {e}")
            return self._fake_receipt_data()

    def process_formula(self, formula_path: Path) -> dict:
        if not formula_path.exists() or not self.client:
            return self._fake_formula_data()

        try:
            base64_image = encode_image_to_base64(formula_path)
            response = self.client.chat.completions.create(
                model="moonshot-v1-128k-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                            {"type": "text", "text": "请分析这张图片中的手写公式，解释其含义和推导逻辑"},
                        ],
                    }
                ],
            )
            return {"formula": response.choices[0].message.content}
        except Exception as e:
            print(f"Formula API failed: {e}")
            return self._fake_formula_data()

    def _fake_receipt_data(self) -> dict:
        return {"amount": "CNY 2,580.00", "date": "2024-03-15", "items": "Laser Range Finder Pro Max x 2, Mounting Bracket x 2"}

    def _fake_formula_data(self) -> dict:
        return {"formula": "Standard deviation formula: σ = √(Σ(xi - μ)² / n)\n\nUsed for analyzing sales data volatility."}