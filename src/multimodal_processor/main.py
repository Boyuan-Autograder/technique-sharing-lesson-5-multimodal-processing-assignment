import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str | None:
    return os.getenv("MOONSHOT_API_KEY")


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def main():
    project_root = get_project_root()
    data_dir = project_root / "data"
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    has_api_key = bool(get_api_key())

    print("=" * 50)
    print("多模态处理程序启动")
    print(f"API密钥: {'已配置' if has_api_key else '未配置（将使用模拟数据）'}")
    print("=" * 50)

    from multimodal_processor.vision import VisionProcessor
    from multimodal_processor.audio import AudioProcessor
    from multimodal_processor.csv_parser import CSVParser
    from multimodal_processor.report import ReportGenerator

    vision = VisionProcessor()
    audio = AudioProcessor()
    csv_parser = CSVParser()

    receipt_path = data_dir / "receipt.png"
    formula_path = data_dir / "formula.png"
    sales_path = data_dir / "sales.csv"
    audio_path = data_dir / "summary.mp3"

    print("\n[1/4] 处理收据图像...")
    receipt_data = vision.process_receipt(receipt_path)
    print(f"  -> 金额: {receipt_data.get('amount', 'N/A')}")
    print(f"  -> 日期: {receipt_data.get('date', 'N/A')}")

    print("\n[2/4] 处理销售数据...")
    sales_data = csv_parser.analyze_sales(sales_path)
    top_product = sales_data.get("top_product", "N/A")
    print(f"  -> Top1产品: {top_product}")

    print("\n[3/4] 处理公式图像...")
    formula_data = vision.process_formula(formula_path)
    print(f"  -> 公式: {formula_data.get('formula', 'N/A')[:50]}...")

    print("\n[4/4] 处理语音转写...")
    transcript_data = audio.transcribe(audio_path)
    print(f"  -> 转写长度: {len(transcript_data.get('transcript', ''))} 字符")

    print("\n生成报告...")
    report = ReportGenerator()
    report_content = report.generate(
        receipt_data=receipt_data,
        sales_data=sales_data,
        formula_data=formula_data,
        transcript_data=transcript_data,
    )

    output_path = output_dir / "report.md"
    output_path.write_text(report_content, encoding="utf-8")
    print(f"\n报告已生成: {output_path}")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
