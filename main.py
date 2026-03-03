import os
import argparse
import logging
import json
from extractor import DocumentExtractor
from ai_parser import AIParser
from database import DatabaseManager

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_directory(input_dir, model_name="mistral", lang_ocr="fr"):
    """
    Main pipeline to process all PDFs in a directory:
    1. Extract text (native + OCR).
    2. Parse text with local LLM (Ollama) to extract structured JSON.
    3. Save JSON to MongoDB.
    """
    if not os.path.exists(input_dir):
        logger.error(f"Input directory does not exist: {input_dir}")
        return

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        logger.warning(f"No PDF files found in '{input_dir}'.")
        return

    logger.info(f"Found {len(pdf_files)} PDF(s) to process in '{input_dir}'.")

    # Initialize modules
    logger.info("Initializing Extractor (PyMuPDF + PaddleOCR)...")
    extractor = DocumentExtractor(lang_ocr=lang_ocr)

    logger.info(f"Initializing AI Parser with model '{model_name}'...")
    ai_parser = AIParser(model_name=model_name)

    logger.info("Connecting to Database (MongoDB)...")
    db_manager = DatabaseManager()

    success_count = 0
    fail_count = 0

    for filename in pdf_files:
        filepath = os.path.join(input_dir, filename)
        logger.info(f"\nStarting processing for: {filename}\n")

        # Step 1: Extract Text
        logger.info("Step 1: Extracting text...")
        raw_text = extractor.extract_text_from_pdf(filepath)

        if not raw_text or len(raw_text.strip()) == 0:
            logger.error(f"Failed to extract text from {filename}. Skipping.")
            fail_count += 1
            continue

        logger.info(f"Extracted {len(raw_text)} characters from {filename}.")

        # Step 2: Parse with AI
        logger.info("Step 2: Parsing text with AI...")
        structured_data = ai_parser.parse_text(raw_text)

        if not structured_data:
            logger.error(f"AI failed to extract structured data from {filename}. Skipping.")
            fail_count += 1
            continue

        # Save a local copy of the JSON for debugging
        debug_json_path = os.path.join(input_dir, f"{os.path.splitext(filename)[0]}_output.json")
        with open(debug_json_path, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved local JSON copy to {debug_json_path}")

        # Step 3: Save to Database
        logger.info("Step 3: Saving to MongoDB...")
        doc_id = db_manager.insert_document(structured_data, filename)

        if doc_id:
            logger.info(f"Successfully finished processing {filename}. DB ID: {doc_id}")
            success_count += 1
        else:
            logger.error(f"Failed to save data for {filename} to database.")
            fail_count += 1

    # Cleanup
    db_manager.close()

    logger.info(f"\n{'='*50}\nProcessing Complete!")
    logger.info(f"Successfully processed: {success_count}/{len(pdf_files)}")
    logger.info(f"Failed: {fail_count}/{len(pdf_files)}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DGI Unstructured Data Extraction Pipeline")
    parser.add_argument("--input", type=str, default="./input_documents", help="Directory containing PDF files to process.")
    parser.add_argument("--model", type=str, default="mistral", help="Ollama model name to use (e.g., mistral, llama3).")
    parser.add_argument("--lang", type=str, default="fr", help="Language for OCR (fr, en, ar).")

    args = parser.parse_args()

    # Create input directory if it doesn't exist to prevent immediate crash on first run
    if not os.path.exists(args.input):
        os.makedirs(args.input)
        logger.info(f"Created input directory '{args.input}'. Place your PDF files here.")

    process_directory(args.input, model_name=args.model, lang_ocr=args.lang)
