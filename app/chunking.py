from pathlib import Path
import json
import re
import shutil


# =========================================================
# PATHS
# =========================================================

CLEANED_DIR = Path("data/cleaned")
CHUNKS_DIR = Path("data/chunks")

CHUNK_SIZE = 1400


# =========================================================
# AGE METADATA
# =========================================================

def detect_age_metadata(text):
    """
    Detect age information only when it is explicitly
    mentioned in the chunk.

    Returns:
        age_group
        age_scope
    """

    text_lower = text.lower()

    # 2-59 months
    if re.search(
        r"\b2\s*[-–]\s*59\s*months?\b",
        text_lower
    ):
        return (
            "child_2_59_months",
            "2-59 months"
        )

    # 5-9 years
    if re.search(
        r"\b5\s*[-–]\s*9\s*years?\b",
        text_lower
    ):
        return (
            "child_5_9_years",
            "5-9 years"
        )

    # 10-14 years
    if re.search(
        r"\b10\s*[-–]\s*14\s*years?\b",
        text_lower
    ):
        return (
            "child_10_14_years",
            "10-14 years"
        )

    # Up to 10 years
    if re.search(
        r"\bup\s*to\s*10\s*years?\b",
        text_lower
    ):
        return (
            "up_to_10_years",
            "up to 10 years"
        )

    # Young infant
    if re.search(
        r"\byoung infant\b",
        text_lower
    ):
        return (
            "young_infant",
            "up to 2 months"
        )

    # Newborn / neonate
    if (
        re.search(r"\bnewborn\b", text_lower)
        or
        re.search(r"\bneonate\b", text_lower)
        or
        re.search(r"\bneonates\b", text_lower)
    ):
        return (
            "newborn",
            "newborn/neonate"
        )

    # No reliable age information
    return None, None


# =========================================================
# MARKDOWN HEADING DETECTION
# =========================================================

def is_markdown_heading(line):
    return bool(
        re.match(
            r"^#{1,6}\s+",
            line.strip()
        )
    )


# =========================================================
# SPLIT LARGE TEXT
# =========================================================

def split_large_text(text):

    paragraphs = re.split(
        r"\n\s*\n",
        text
    )

    chunks = []
    current = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # Paragraph fits into current chunk
        if (
            len(current)
            + len(paragraph)
            + 2
            <= CHUNK_SIZE
        ):

            current = (
                f"{current}\n\n{paragraph}"
            ).strip()

        else:

            # Save current chunk
            if current:
                chunks.append(current)

            # Paragraph itself is too large
            if len(paragraph) > CHUNK_SIZE:

                words = paragraph.split()

                current = ""

                for word in words:

                    if (
                        len(current)
                        + len(word)
                        + 1
                        <= CHUNK_SIZE
                    ):

                        current += (
                            (" " if current else "")
                            + word
                        )

                    else:

                        if current:
                            chunks.append(current)

                        current = word

            else:

                current = paragraph

    # Save final chunk
    if current:
        chunks.append(current)

    return chunks


# =========================================================
# CREATE CHUNKS FOR A PAGE
# =========================================================

def create_chunks(
    page_text,
    page_number,
    document_id,
    file_path
):

    lines = page_text.splitlines()

    sections = []
    current = []

    # Keep headings attached to their following content
    for line in lines:

        line = line.strip()

        if not line:
            continue

        if is_markdown_heading(line):

            if current:
                sections.append(
                    "\n".join(current)
                )

                current = []

            current.append(line)

        else:

            current.append(line)

    # Save final section
    if current:
        sections.append(
            "\n".join(current)
        )

    chunks = []

    chunk_number = 1

    for section in sections:

        pieces = split_large_text(section)

        for piece in pieces:

            if not piece.strip():
                continue

            # Detect age only if explicitly present
            age_group, age_scope = (
                detect_age_metadata(piece)
            )

            chunk = {

                "chunk_id": (
                    f"{document_id}_"
                    f"p{page_number}_"
                    f"c{chunk_number:02d}"
                ),

                "text": piece.strip(),

                "metadata": {

                    "document_id": document_id,

                    "page_number": page_number,

                    "file_path": file_path,

                    "age_group": age_group,

                    "age_scope": age_scope
                }
            }

            chunks.append(chunk)

            chunk_number += 1

    return chunks


# =========================================================
# PROCESS ONE JSON FILE
# =========================================================

def process_file(json_path):

    with open(
        json_path,
        "r",
        encoding="utf-8"
    ) as file:

        pages = json.load(file)

    document_id = json_path.stem

    all_chunks = []

    for page in pages:

        # Page number is inside metadata
        page_number = page.get(
            "metadata",
            {}
        ).get(
            "page_number",
            0
        )

        text = page.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        chunks = create_chunks(
            page_text=text,
            page_number=page_number,
            document_id=document_id,
            file_path=str(json_path)
        )

        all_chunks.extend(chunks)

    # Output file
    output_path = (
        CHUNKS_DIR / json_path.name
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    # =====================================================
    # AGE METADATA STATISTICS
    # =====================================================

    age_counts = {}

    for chunk in all_chunks:

        age_group = chunk["metadata"].get(
            "age_group"
        )

        if age_group is None:
            age_group = "none"

        age_counts[age_group] = (
            age_counts.get(
                age_group,
                0
            ) + 1
        )

    print(
        f"\n{json_path.name}: "
        f"{len(all_chunks)} chunks"
    )

    print("Age metadata:")

    for age_group, count in sorted(
        age_counts.items()
    ):

        print(
            f"  {age_group}: {count}"
        )

    return len(all_chunks)


# =========================================================
# MAIN
# =========================================================

def main():

    # Rebuild chunks from scratch
    if CHUNKS_DIR.exists():

        print(
            f"Removing old directory: "
            f"{CHUNKS_DIR}"
        )

        shutil.rmtree(CHUNKS_DIR)

    CHUNKS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Find cleaned files
    json_files = sorted(
        CLEANED_DIR.glob("*.json")
    )

    print(
        f"Found {len(json_files)} "
        f"cleaned files"
    )

    total = 0

    for json_path in json_files:

        total += process_file(
            json_path
        )

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print("\n" + "=" * 60)

    print(
        f"Total chunks: {total}"
    )

    print(
        f"Output directory: {CHUNKS_DIR}"
    )

    print("=" * 60)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()