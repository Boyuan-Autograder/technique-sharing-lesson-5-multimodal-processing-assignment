import pytest
from pathlib import Path
from multimodal_processor.vision import VisionProcessor
from multimodal_processor.audio import AudioProcessor
from multimodal_processor.csv_parser import CSVParser
from multimodal_processor.report import ReportGenerator


class TestVisionProcessor:
    def setup_method(self):
        self.processor = VisionProcessor()

    def test_fake_receipt_data(self):
        result = self.processor._fake_receipt_data()
        assert "amount" in result
        assert "date" in result
        assert "CNY" in result["amount"]

    def test_fake_formula_data(self):
        result = self.processor._fake_formula_data()
        assert "formula" in result
        assert "σ" in result["formula"] or "标准差" in result["formula"]


class TestAudioProcessor:
    def setup_method(self):
        self.processor = AudioProcessor()

    def test_fake_transcript_data(self):
        result = self.processor._fake_transcript_data()
        assert "transcript" in result
        assert "key_points" in result
        assert len(result["key_points"]) > 0

    def test_transcript_has_key_points(self):
        result = self.processor._fake_transcript_data()
        assert isinstance(result["key_points"], list)
        assert len(result["transcript"]) > 100


class TestCSVParser:
    def setup_method(self):
        self.parser = CSVParser()

    def test_fake_sales_data(self):
        result = self.parser._fake_sales_data()
        assert "top_product" in result
        assert "total_revenue" in result
        assert "智能传感器" in result["top_product"]

    def test_sales_data_has_ranking(self):
        result = self.parser._fake_sales_data()
        assert "product_ranking" in result
        assert isinstance(result["product_ranking"], dict)


class TestReportGenerator:
    def setup_method(self):
        self.generator = ReportGenerator()
        self.fake_data = {
            "receipt_data": {"amount": "¥2,580.00", "date": "2024-03-15", "items": "测试商品"},
            "sales_data": {
                "top_product": "智能传感器Pro",
                "top_product_sales": 312000,
                "total_revenue": 1000000,
                "product_ranking": {"智能传感器Pro": 312000, "激光测距仪Max": 100000},
            },
            "formula_data": {"formula": "σ = √(Σ(xi - μ)² / n)"},
            "transcript_data": {
                "transcript": "测试转写文本",
                "key_points": ["观点1", "观点2"],
                "decisions": ["决策1"],
            },
        }

    def test_generate_report(self):
        report = self.generator.generate(**self.fake_data)
        assert "季度业务简报" in report
        assert "财务摘要" in report
        assert "智能传感器Pro" in report

    def test_report_contains_all_sections(self):
        report = self.generator.generate(**self.fake_data)
        assert "一、财务摘要" in report
        assert "二、经营亮点" in report
        assert "三、技术细节" in report
        assert "四、决策录音" in report

    def test_percentage_calculation(self):
        pct = self.generator._calculate_percentage(self.fake_data["sales_data"])
        assert pct == pytest.approx(31.2, rel=0.1)
