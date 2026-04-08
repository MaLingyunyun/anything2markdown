from __future__ import annotations

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions, TableStructureOptions
from docling.document_converter import DocumentConverter, ImageFormatOption, PdfFormatOption


def build_doc_converter() -> DocumentConverter:
    """复用原脚本 OCR+表格能力。"""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options = TableStructureOptions(do_cell_matching=True)
    pipeline_options.ocr_options = RapidOcrOptions(force_full_page_ocr=True)

    return DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.IMAGE,
            InputFormat.DOCX,
            InputFormat.PPTX,
            InputFormat.XLSX,
            InputFormat.HTML,
            InputFormat.MD,
            InputFormat.CSV,
            InputFormat.ASCIIDOC,
            InputFormat.LATEX,
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options),
        },
    )
