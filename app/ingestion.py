from pathlib import Path  # to work with path
import json

import pymupdf4llm


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def extract_pdf(pdf_path: Path):             
    return pymupdf4llm.to_markdown(
        pdf_path,
        page_chunks=True
    )


def save_extracted_data(pdf_path: Path, pages):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_name = pdf_path.stem + ".json"                  #name with json exstintion , 
                                                           #without steam it will looks like (dta.pdf.joson)
    output_path = PROCESSED_DIR / output_name

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            pages,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"Saved: {output_path}")


def main():
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files")

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")

        pages = extract_pdf(pdf_path)

        print(f"Extracted pages: {len(pages)}")

        save_extracted_data(pdf_path, pages)


if __name__ == "__main__":
    main()