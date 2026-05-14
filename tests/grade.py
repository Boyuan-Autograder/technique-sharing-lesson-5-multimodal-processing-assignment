"""
GitHub Classroom 自动评分脚本

评分为 4 个维度，每项 25 分（满分 100）：
  财务摘要 (25分) — 收据金额、日期
  经营亮点 (25分) — Top1 产品识别
  技术细节 (25分) — 公式解析
  决策录音 (25分) — 转写文本、核心观点

策略：对确定性内容做精确检查，对 API 依赖内容做存在性检查。
"""
import sys
import json
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Force UTF-8 on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ── 工具函数 ────────────────────────────────────────────

def print_grade(category: str, score: int, max_score: int, detail: str = ""):
    if max_score > 0:
        bar = "#" * (score * 20 // max_score) + "-" * (20 - score * 20 // max_score)
    else:
        bar = "#" * 20
    print(f"  [{bar}] {category}: {score}/{max_score}  {detail}")


def make_testcase(name: str, classname: str, passed: bool, message: str = "") -> Element:
    tc = Element("testcase", {"name": name, "classname": classname})
    if not passed:
        SubElement(tc, "failure", {"message": message}).text = message
    return tc


def write_junit(suite_name: str, testcases: list[Element], outpath: str):
    suite = Element("testsuite", {
        "name": suite_name,
        "tests": str(len(testcases)),
        "failures": str(sum(1 for t in testcases if t.find("failure") is not None)),
    })
    for tc in testcases:
        suite.append(tc)
    raw_xml = tostring(suite, encoding="utf-8")
    import xml.dom.minidom as mdom
    xml = mdom.parseString(raw_xml).toprettyxml(indent="  ", encoding="utf-8")
    Path(outpath).write_bytes(xml)


# ── 主评分逻辑 ──────────────────────────────────────────

def main():
    root = Path(__file__).parent.parent
    data_dir = root / "data"
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)

    print("=" * 50)
    print("GitHub Classroom 自动评分")
    print("=" * 50)

    testcases = []

    # ---------- 检查 1：代码是否可运行 ----------
    print("\n[前置检查] 运行处理管线...")
    import_code_ok = False
    run_error = None
    try:
        from multimodal_processor.vision import VisionProcessor, encode_image_to_base64, get_api_key
        from multimodal_processor.audio import AudioProcessor
        from multimodal_processor.csv_parser import CSVParser
        from multimodal_processor.report import ReportGenerator
        import_code_ok = True
        print("  导入成功")
    except Exception as e:
        run_error = str(e)
        print(f"  导入失败: {e}")

    if import_code_ok:
        try:
            vision = VisionProcessor()
            audio = AudioProcessor()
            csv_parser = CSVParser()
            report_gen = ReportGenerator()

            receipt_data = vision.process_receipt(data_dir / "receipt.png")
            sales_data = csv_parser.analyze_sales(data_dir / "sales.csv")
            formula_data = vision.process_formula(data_dir / "formula.png")
            transcript_data = audio.transcribe(data_dir / "summary.mp3")

            report = report_gen.generate(receipt_data, sales_data, formula_data, transcript_data)
            (output_dir / "report.md").write_text(report, encoding="utf-8")
            print("  管线运行成功")
            run_error = None
        except Exception as e:
            run_error = str(e)
            print(f"  管线运行失败: {e}")

    if run_error:
        print(f"\n[!!] 程序无法运行: {run_error}")
        testcases = [
            make_testcase("管线可运行", "前置检查", False, run_error),
        ]
        write_junit("Autograding", testcases, str(root / "grading-results.xml"))
        print("\n总分: 0/100 (程序未能运行)")
        return 1

    testcases.append(make_testcase("管线可运行", "前置检查", True))
    print_grade("管线可运行", 0, 0, "前置条件")

    # ---------- 读取报告 ----------
    try:
        report_path = output_dir / "report.md"
        report_text = report_path.read_text(encoding="utf-8")
        print(f"\n  报告大小: {len(report_text)} 字符")
    except Exception as e:
        print(f"  无法读取报告: {e}")
        testcases = [make_testcase("管线可运行", "前置检查", True)]
        testcases.append(make_testcase("报告生成", "前置检查", False, str(e)))
        write_junit("Autograding", testcases, str(root / "grading-results.xml"))
        print("\n总分: 0/100")
        return 1

    # ────────── 评分维度 ──────────
    total = 0

    # ====== 财务摘要 (25分) ======
    print("\n--- 1. 财务摘要 (满分 25) ---")
    finance_ok = True

    # 1a. 报告包含「财务摘要」章节 (5分)
    if "财务摘要" in report_text:
        print_grade("章节存在", 5, 5)
        total += 5
    else:
        print_grade("章节存在", 0, 5, "报告中未找到「财务摘要」章节")
        finance_ok = False

    # 1b. 收据金额字段存在 (10分)
    amount_ok = "金额" in report_text or "amount" in report_text.lower()
    if amount_ok:
        print_grade("金额字段", 10, 10)
        total += 10
    else:
        print_grade("金额字段", 0, 10, "报告中未找到金额信息")
        finance_ok = False

    # 1c. 日期字段存在 (10分)
    # 检查是否有日期格式（YYYY-MM-DD 或 YYYY/MM/DD 等）
    import re
    has_date = bool(re.search(r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}", report_text))
    if has_date or "日期" in report_text or "date" in report_text.lower():
        print_grade("日期字段", 10, 10)
        total += 10
    else:
        print_grade("日期字段", 0, 10, "报告中未找到日期信息")
        finance_ok = False

    testcases.append(make_testcase("财务摘要", "评分项", finance_ok,
        f"{25 if finance_ok else 5 if amount_ok else 0}/25"))

    # ====== 经营亮点 (25分) ======
    print("\n--- 2. 经营亮点 (满分 25) ---")
    sales_ok = True

    # 2a. 报告识别出 Top1 产品 (15分) — 确定性检查
    expected_product = "智能传感器Pro"
    if expected_product in report_text or "智能传感器" in report_text:
        print_grade("Top1 产品识别", 15, 15, f"→ {expected_product}")
        total += 15
    else:
        print_grade("Top1 产品识别", 0, 15, f"期望包含 '{expected_product}'，但未找到")
        sales_ok = False

    # 2b. 产品排行存在 (10分)
    has_ranking = "排行" in report_text or "ranking" in report_text.lower()
    has_multiple_products = report_text.count("智能传感器") + report_text.count("激光") + report_text.count("红外") >= 3
    if has_ranking and has_multiple_products:
        print_grade("产品排行", 10, 10)
        total += 10
    elif has_ranking:
        print_grade("产品排行", 5, 10, "排行存在但可能不完整")
        total += 5
    else:
        print_grade("产品排行", 0, 10, "未找到产品排行信息")
        sales_ok = False

    testcases.append(make_testcase("经营亮点", "评分项", sales_ok,
        f"{25 if sales_ok else 15 if expected_product in report_text else 0}/25"))

    # ====== 技术细节 (25分) ======
    print("\n--- 3. 技术细节 (满分 25) ---")
    formula_ok = True

    # 3a. 包含「技术细节」或「公式」章节 (5分)
    if "技术细节" in report_text or "公式" in report_text:
        print_grade("章节存在", 5, 5)
        total += 5
    else:
        print_grade("章节存在", 0, 5)
        formula_ok = False

    # 3b. 包含公式解释内容（足够长的文本）(10分)
    formula_section_start = report_text.find("技术细节")
    if formula_section_start > 0:
        formula_section = report_text[formula_section_start:formula_section_start + 2000]
    else:
        formula_section = report_text
    if len(formula_section) > 100:
        print_grade("公式解释内容", 10, 10)
        total += 10
    else:
        print_grade("公式解释内容", 0, 10, "公式解释内容过短或缺失")
        formula_ok = False

    # 3c. 包含数学符号或公式标记 (10分)
    has_math = any(
        sym in report_text
        for sym in ["σ", "∑", "√", "μ", "\\sigma", "\\sum", "\\sqrt", "LaTeX", "标准差", "公式"]
    )
    if has_math:
        print_grade("数学符号/公式", 10, 10)
        total += 10
    else:
        print_grade("数学符号/公式", 0, 10, "未检测到数学符号或公式说明")
        formula_ok = False

    testcases.append(make_testcase("技术细节", "评分项", formula_ok,
        f"{25 if formula_ok else 15 if has_math else 0}/25"))

    # ====== 决策录音 (25分) ======
    print("\n--- 4. 决策录音 (满分 25) ---")
    audio_ok = True

    # 4a. 包含「决策录音」或「录音」章节 (5分)
    if "决策录音" in report_text or "录音" in report_text:
        print_grade("章节存在", 5, 5)
        total += 5
    else:
        print_grade("章节存在", 0, 5)
        audio_ok = False

    # 4b. 包含转写文本（足够长度）(10分)
    # 找转写文本所在区域，检查长度
    transcript_start = report_text.find("转写文本")
    if transcript_start > 0:
        transcript_area = report_text[transcript_start:transcript_start + 3000]
    else:
        transcript_area = report_text
    if len(transcript_area) > 100:
        print_grade("转写文本", 10, 10)
        total += 10
    else:
        print_grade("转写文本", 0, 10, "转写文本缺失或过短")
        audio_ok = False

    # 4c. 包含「核心观点」或「关键决策」(10分)
    has_key_points = "核心观点" in report_text or "关键决策" in report_text or "key_point" in report_text.lower()
    if has_key_points:
        print_grade("核心观点/决策", 10, 10)
        total += 10
    else:
        print_grade("核心观点/决策", 0, 10, "未找到核心观点或关键决策")
        audio_ok = False

    testcases.append(make_testcase("决策录音", "评分项", audio_ok,
        f"{25 if audio_ok else 15 if has_key_points else 0}/25"))

    # ────────── 汇总 ──────────
    print("\n" + "=" * 50)
    bar = "#" * (total // 5) + "-" * (20 - total // 5)
    print(f"  [{bar}] 总分: {total}/100 ({total / 100:.0%})")
    print("=" * 50)

    write_junit("Autograding", testcases, str(root / "grading-results.xml"))
    return 0 if total >= 60 else 1


if __name__ == "__main__":
    sys.exit(main())
