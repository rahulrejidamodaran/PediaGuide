from pathlib import Path
import json

from langchain_huggingface import HuggingFaceEmbeddings


CHUNKS_DIR = Path("data/chunks")
EMBEDDINGS_DIR = Path("data/embeddings")

MODEL_NAME = "BAAI/bge-small-en-v1.5"


def main():

    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME
    )

    chunk_files = sorted(CHUNKS_DIR.glob("*.json"))

    print(f"Found {len(chunk_files)} chunk files")

    for chunk_file in chunk_files:

        print(f"\nEmbedding: {chunk_file.name}")

        with open(chunk_file, "r", encoding="utf-8") as file:
            chunks = json.load(file)

        texts = [chunk["text"] for chunk in chunks]

        print(f"Chunks: {len(texts)}")

        vectors = embeddings.embed_documents(texts)

        embedded_chunks = []

        for chunk, vector in zip(chunks, vectors):

            embedded_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "vector": vector,
                "metadata": chunk["metadata"]
            })

        output_file = EMBEDDINGS_DIR / chunk_file.name

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(
                embedded_chunks,
                file,
                ensure_ascii=False,
                indent=2
            )

        print(f"Saved: {output_file}")
        print(f"Vectors created: {len(vectors)}")


if __name__ == "__main__":
    main()