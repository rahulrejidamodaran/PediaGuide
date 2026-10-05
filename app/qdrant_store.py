from pathlib import Path
import json
import uuid

from qdrant_client import QdrantClient, models


# V2 paths
EMBEDDINGS_DIR = Path("data/embeddings")
QDRANT_DIR = Path("data/qdrant")
COLLECTION_NAME = "pediaguide"

VECTOR_SIZE = 384


def create_client():
    return QdrantClient(path=str(QDRANT_DIR))


def create_collection(client):
    if client.collection_exists(COLLECTION_NAME):
        print(f"Collection already exists: {COLLECTION_NAME}")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE,
        ),
    )

    print(f"Created collection: {COLLECTION_NAME}")


def load_embedding_file(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def create_point_id(chunk):
    unique_id = (
        f"{chunk['metadata']['document_id']}|"
        f"{chunk['chunk_id']}"
    )

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            unique_id
        )
    )


def insert_embeddings(client):
    json_files = sorted(EMBEDDINGS_DIR.glob("*.json"))

    total_inserted = 0

    for json_path in json_files:

        chunks = load_embedding_file(json_path)

        points = []

        for chunk in chunks:

            point = models.PointStruct(
                id=create_point_id(chunk),

                vector=chunk["vector"],

                payload={
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    **chunk["metadata"],
                },
            )

            points.append(point)

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True,
        )

        total_inserted += len(points)

        print(
            f"{json_path.name}: "
            f"{len(points)} points inserted"
        )

    print(f"\nTotal points inserted: {total_inserted}")


def main():

    QDRANT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    client = create_client()

    create_collection(client)

    insert_embeddings(client)

    collection_info = client.get_collection(
        COLLECTION_NAME
    )

    print("\nQdrant collection information:")
    print(collection_info)

    client.close()


if __name__ == "__main__":
    main()