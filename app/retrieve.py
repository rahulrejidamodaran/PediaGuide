# ============================================================
# PediaGuide AI - Medical Evidence Retrieval
# ============================================================

from qdrant_client import QdrantClient, models
from langchain_huggingface import HuggingFaceEmbeddings


# ============================================================
# 1. SETTINGS
# ============================================================

QDRANT_FOLDER = "data/qdrant"
COLLECTION_NAME = "pediaguide"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


# ============================================================
# 2. CONNECT TO QDRANT
# ============================================================

qdrant = QdrantClient(
    path=QDRANT_FOLDER
)


embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


# ============================================================
# 3. CONVERT AGE INTO AN AGE GROUP
# ============================================================

def get_age_group(age_months):
    """
    Convert the child's age into the age groups
    used by our medical knowledge base.
    """

    if age_months < 2:
        return "young_infant"

    if age_months < 60:
        return "child_2_59_months"

    if age_months < 120:
        return "child_5_9_years"

    if age_months < 180:
        return "child_10_14_years"

    return "adolescent_15_years"


# ============================================================
# 4. SEARCH MEDICAL EVIDENCE
# ============================================================

def retrieve_evidence(
    question,
    age_months,
    limit=5
):
    """
    Find the most relevant medical information
    for the user's question and child's age.
    """

    # --------------------------------------------------------
    # Step 1: Find the age group
    # --------------------------------------------------------

    age_group = get_age_group(
        age_months
    )


    # --------------------------------------------------------
    # Step 2: Add the age group to the search
    # --------------------------------------------------------

    search_query = (
        f"{age_group}: {question}"
    )


    # --------------------------------------------------------
    # Step 3: Convert question into an embedding
    # --------------------------------------------------------

    query_vector = embeddings.embed_query(
        search_query
    )


    # --------------------------------------------------------
    # Step 4: Only retrieve:
    #
    #       - chunks for this age group
    #       - general chunks without an age group
    # --------------------------------------------------------

    age_filter = models.Filter(

        should=[

            models.FieldCondition(
                key="age_group",
                match=models.MatchValue(
                    value=age_group
                )
            ),

            models.IsNullCondition(
                is_null=models.PayloadField(
                    key="age_group"
                )
            )
        ]
    )


    # --------------------------------------------------------
    # Step 5: Search Qdrant
    # --------------------------------------------------------

    results = qdrant.query_points(

        collection_name=COLLECTION_NAME,

        query=query_vector,

        query_filter=age_filter,

        limit=limit
    ).points


    return results


# ============================================================
# 5. CLOSE QDRANT
# ============================================================

def close_retriever():
    """
    Close the Qdrant connection.
    """

    qdrant.close()