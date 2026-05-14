import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8 output on Windows terminals
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"


def get_api_key() -> str | None:
    return os.getenv("MOONSHOT_API_KEY") or os.getenv("KIMI_API_KEY")


def print_separator(title: str = ""):
    width = 60
    if title:
        print(f"\n{'-' * width}")
        print(f"  {title}")
        print(f"{'-' * width}")
    else:
        print(f"{'-' * width}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    api_key = get_api_key()
    has_api = bool(api_key)

    print("=" * 60)
    print("  多模态混合文件解析系统")
    print("  Multimodal Document Processor")
    print("=" * 60)
    print(f"  API Key (Kimi): {'[OK] 已配置' if has_api else '[!!] 未配置（使用模拟数据）'}")
    print(f"  数据目录: {DATA_DIR}")
    print(f"  输出目录: {OUTPUT_DIR}")

    from multimodal_processor.vision import VisionProcessor
    from multimodal_processor.audio import AudioProcessor
    from multimodal_processor.csv_parser import CSVParser
    from multimodal_processor.report import ReportGenerator

    vision = VisionProcessor()
    audio = AudioProcessor()
    csv_parser = CSVParser()

    receipt_path = DATA_DIR / "receipt.png"
    formula_path = DATA_DIR / "formula.png"
    sales_path = DATA_DIR / "sales.csv"
    audio_path = DATA_DIR / "summary.mp3"

    # Step 1: Receipt
    print_separator("[1/4] 收据图像识别 (Kimi Vision API)")
    receipt_data = vision.process_receipt(receipt_path)
    print(f"  [+] 金额: {receipt_data.get('amount', 'N/A')}")
    print(f"  [+] 日期: {receipt_data.get('date', 'N/A')}")
    if receipt_data.get("items"):
        print(f"  [+] 商品: {receipt_data['items']}")

    # Step 2: Sales CSV
    print_separator("[2/4] 销售数据分析 (Pandas)")
    sales_data = csv_parser.analyze_sales(sales_path)
    top_product = sales_data.get("top_product", "N/A")
    top_sales = sales_data.get("top_product_sales", 0)
    total_rev = sales_data.get("total_revenue", 0)
    print(f"  [+] Top1 产品: {top_product}")
    print(f"  [+] 单品总销售额: CNY {top_sales:,.0f}")
    print(f"  [+] 总营收: CNY {total_rev:,.0f}")
    print(f"  [+] 交易笔数: {sales_data.get('total_transactions', 0)}")

    # Step 3: Formula
    print_separator("[3/4] 手写公式识别 (Kimi Vision API)")
    formula_data = vision.process_formula(formula_path)
    formula_text = formula_data.get("formula", "N/A")
    formula_preview = formula_text[:120].replace("\n", " ") + "..."
    print(f"  [+] 公式解析: {formula_preview}")

    # Step 4: Audio
    print_separator("[4/4] 语音转写 (Faster-Whisper + Kimi)")
    transcript_data = audio.transcribe(audio_path)
    t_len = len(transcript_data.get("transcript", ""))
    kp_count = len(transcript_data.get("key_points", []))
    print(f"  [+] 转写文本: {t_len} 字符")
    print(f"  [+] 核心观点: {kp_count} 条")
    if transcript_data.get("decisions"):
        print(f"  [+] 关键决策: {len(transcript_data['decisions'])} 项")

    # Generate report
    print_separator("生成报告")
    report = ReportGenerator()
    report_content = report.generate(
        receipt_data=receipt_data,
        sales_data=sales_data,
        formula_data=formula_data,
        transcript_data=transcript_data,
    )

    output_path = OUTPUT_DIR / "report.md"
    output_path.write_text(report_content, encoding="utf-8")
    print(f"  [+] 报告已生成: {output_path}")
    print(f"  [+] 报告大小: {len(report_content):,} 字符")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
