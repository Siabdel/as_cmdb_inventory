# backend/scanner/services/__init__.py
"""
Services pour le module Scanner.
"""

from .pdf_generator import generate_label_pdf, PDFLabelGenerator

__all__ = ['generate_label_pdf', 'PDFLabelGenerator']
