from pathlib import Path
import json
import re
import unicodedata


PROCESSED_DIR = Path("data/processed")
CLEANED_DIR = Path("data/cleaned")


def clean_text(text):
    """Clean extracted text without removing meaningful medical symbols."""

    if not text:
        return ""

    # Remove HTML-style tags such as <u>
    text = re.sub(r"<[^>]+>", "", text)

    # Remove image extraction markers
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Normalize Unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Normalize different types of spaces
    text = text.replace("\u00a0", " ")

    # Remove spaces before punctuation
    text = re.sub(r"[ \t]+([,.;:!?])", r"\1", text)

    # Remove excessive spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Clean every line
    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Ignore lines containing only decorative characters
        if re.fullmatch(r"[\W_]+", line, flags=re.UNICODE):
            continue

        lines.append(line)

    return "\n".join(lines).strip()


def is_page_number_only(text):
    """Remove pages containing only a page number."""

    text = text.strip()

    if re.fullmatch(r"\d+", text):
        return True

    # Roman numerals used in front matter
    if re.fullmatch(r"[IVXLCDM]+", text, flags=re.IGNORECASE):
        return True

    return False


def is_meaningful_page(text):
    """Keep pages that contain actual textual information."""

    if not text:
        return False

    if is_page_number_only(text):
        return False

    # Remove pages containing no alphabetic characters
    if not re.search(r"[A-Za-z]", text):
        return False

    return True


def clean_document(json_path):
    """Clean one extracted JSON document."""

    with open(json_path, "r", encoding="utf-8") as file:
        pages = json.load(file)

    cleaned_pages = []

    for page in pages:

        raw_text = page.get("text", "")
        text = clean_text(raw_text)

        if not is_meaningful_page(text):
            continue

        metadata = page.get("metadata", {})

        cleaned_page = {
            "text": text,
            "metadata": {
                "page_number": metadata.get("page_number"),
                "page_count": metadata.get("page_count"),
                "file_path": metadata.get("file_path")
            }
        }

        cleaned_pages.append(cleaned_page)

    return cleaned_pages


def main():

    CLEANED_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(PROCESSED_DIR.glob("*.json"))

    print(f"Found {len(json_files)} extracted documents")

    for json_path in json_files:

        print(f"\nCleaning: {json_path.name}")

        cleaned_pages = clean_document(json_path)

        output_path = CLEANED_DIR / json_path.name

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(
                cleaned_pages,
                file,
                ensure_ascii=False,
                indent=2
            )

        print(f"Pages kept: {len(cleaned_pages)}")
        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()