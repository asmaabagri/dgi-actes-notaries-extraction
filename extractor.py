import os
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import logging

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentExtractor:
    def __init__(self, lang_ocr='fr'):
        """
        Initialize the Document Extractor.

        Args:
            lang_ocr (str): The language parameter for PaddleOCR ('fr' for French, 'en' for English, 'ar' for Arabic).
                            For mixed documents, you might need to experiment or run multiple passes if PaddleOCR
                            doesn't support mixed out-of-the-box well for your specific combo.
        """
        logger.info(f"Initializing PaddleOCR with language: {lang_ocr}")
        # Initialize PaddleOCR
        # use_angle_cls=True is useful for rotated documents
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang_ocr, show_log=False)

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts text from a PDF file.
        It tries to extract native text first. If a page has very little text (likely a scanned image),
        it falls back to OCR using PaddleOCR.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: The fully extracted text from the document.
        """
        if not os.path.exists(pdf_path):
            logger.error(f"File not found: {pdf_path}")
            return None

        logger.info(f"Processing PDF: {pdf_path}")
        extracted_text = ""

        try:
            # Open the PDF file
            doc = fitz.open(pdf_path)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Attempt to extract native text
                native_text = page.get_text().strip()

                # Heuristic: If native text is less than 50 characters, it might be a scanned page or an image
                if len(native_text) < 50:
                    logger.info(f"Page {page_num + 1} seems to be a scan or image. Falling back to OCR.")

                    # Convert PDF page to an image (pixmap)
                    # matrix=fitz.Matrix(2, 2) increases resolution for better OCR
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

                    # Save image temporarily (or pass bytes directly if supported, but saving is safer for PaddleOCR)
                    temp_img_path = f"temp_page_{page_num}.png"
                    pix.save(temp_img_path)

                    # Run OCR on the image
                    ocr_result = self.ocr.ocr(temp_img_path, cls=True)

                    page_text = ""
                    # ocr_result is a list of lists.
                    # Usually: [[[box coordinates], (text, confidence)], ...]
                    if ocr_result and ocr_result[0]:
                        for line in ocr_result[0]:
                            text = line[1][0]
                            page_text += text + "\n"

                    extracted_text += f"\n--- Page {page_num + 1} (OCR) ---\n" + page_text

                    # Clean up temporary image
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)

                else:
                    logger.info(f"Page {page_num + 1} contains native text. Extracting directly.")
                    extracted_text += f"\n--- Page {page_num + 1} ---\n" + native_text

            doc.close()
            return extracted_text.strip()

        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return None

if __name__ == "__main__":
    # Simple test (you need a dummy PDF to test)
    # extractor = DocumentExtractor(lang_ocr='fr')
    # text = extractor.extract_text_from_pdf("sample.pdf")
    # print(text)
    pass
