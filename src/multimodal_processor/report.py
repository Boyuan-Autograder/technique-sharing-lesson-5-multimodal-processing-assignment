from typing import Any


class ReportGenerator:
    def generate(
        self,
        receipt_data: dict,
        sales_data: dict,
        formula_data: dict,
        transcript_data: dict,
    ) -> str:
        report = f"""# 季度业务简报

> 数据来源：多模态混合文件包解析

---

## 1. 财务摘要

| 项目 | 内容 |
|------|------|
| 收据金额 | {receipt_data.get('amount', 'N/A')} |
| 业务发生日期 | {receipt_data.get('date', 'N/A')} |
| 商品明细 | {receipt_data.get('items', 'N/A')} |

---

## 2. 经营亮点

### 销售额 Top1 产品

**{sales_data.get('top_product', 'N/A')}**

- 销售额：¥{sales_data.get('top_product_sales', 0):,}
- 占总营收比例：{self._calculate_percentage(sales_data):.1f}%

### 产品销售排行

{self._format_product_ranking(sales_data.get('product_ranking', {}))}

---

## 3. 技术细节

### 公式解析

{formula_data.get('formula', 'N/A')}

---

## 4. 决策录音

### 完整转写文本

{transcript_data.get('transcript', 'N/A')}

### 核心观点

{self._format_key_points(transcript_data.get('key_points', []))}

### 关键决策

{self._format_decisions(transcript_data.get('decisions', []))}

---

## 附录：原始数据

### 销售数据表

{sales_data.get('markdown_table', 'N/A')}

---

*本报告由多模态AI处理程序自动生成*
"""

        return report

    def _calculate_percentage(self, sales_data: dict) -> float:
        top_sales = sales_data.get("top_product_sales", 0)
        total = sales_data.get("total_revenue", 1)
        return (top_sales / total) * 100

    def _format_product_ranking(self, ranking: dict) -> str:
        if not ranking:
            return "无数据"

        lines = []
        for i, (product, sales) in enumerate(ranking.items(), 1):
            lines.append(f"{i}. **{product}** - ¥{sales:,}")
        return "\n".join(lines)

    def _format_key_points(self, key_points: list) -> str:
        if not key_points:
            return "无"

        lines = []
        for point in key_points:
            lines.append(f"- {point}")
        return "\n".join(lines)

    def _format_decisions(self, decisions: list) -> str:
        if not decisions:
            return "无"

        lines = []
        for decision in decisions:
            lines.append(f"- [ ] {decision}")
        return "\n".join(lines)
