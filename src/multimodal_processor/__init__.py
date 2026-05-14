# Lazy imports to avoid circular import issues when running via `python -m`
__all__ = [
    "main",
    "VisionProcessor",
    "AudioProcessor",
    "CSVParser",
    "ReportGenerator",
]
__version__ = "0.1.0"


def __getattr__(name):
    if name == "main":
        from multimodal_processor.main import main
        return main
    if name == "VisionProcessor":
        from multimodal_processor.vision import VisionProcessor
        return VisionProcessor
    if name == "AudioProcessor":
        from multimodal_processor.audio import AudioProcessor
        return AudioProcessor
    if name == "CSVParser":
        from multimodal_processor.csv_parser import CSVParser
        return CSVParser
    if name == "ReportGenerator":
        from multimodal_processor.report import ReportGenerator
        return ReportGenerator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
