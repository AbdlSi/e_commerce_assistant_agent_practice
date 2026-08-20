from typing import Literal
from uuid import uuid4

from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.tools import tool

from dotenv import load_dotenv

from database.models import engine
from sqlalchemy import text
import json

from e_commerce_assistant.tools.product_search import product_search, normalize_filters, extract_filters
load_dotenv()

model = ChatOpenAI(
    model = "gpt-4.1-mini",
    temperature=0,
)

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

recommendation_model_prompt = """
Rules:

- Select products from the provided database products.
-If the users specify the number of products then provide them with the same or closest possible number of products they need.
- select at least 3 products.
- Only recommend products that are present in the provided product data.
- Do not invent products, attributes, prices, ratings, brands, specifications, or availability.
- Do not combine information from multiple products into one recommendation.
- Choose the product that best matches the user's stated needs, preferences, and constraints.
- Prioritize excplicit user requirements such as color, size, category and price.
- If you didn't find a suitable match for these preferences:brand, features(waterproof, sport, etc...), then choose the products that meet his excplicit user requirements such as color, size, category and price.
- Consider relevant factors such as description, category, price, brand, color, size, features, intended use, rating, and other stated preferences.
- Do not automatically choose the cheapest, most expensive, or highest-rated product unless that matches the user's request.
- Return the exact database product row that was selected.
- The returned product_id must exactly match the selected product.
- Identify the user's preferences that are satisfied by the selected product.
- Identify any user preferences that are not satisfied by the selected product.
- Give a concise reason explaining why the selected product is the best option among the provided products.
- Base the recommendation reason only on the provided product data and the user's request.
- Give a confidence score between 0 and 1 representing how strongly the selected product matches the user's requirements.
- If no product perfectly satisfies the user's requirements, select the closest valid product and clearly state the unmet preferences.
- If the available products are insufficient for a meaningful recommendation, return no product instead of inventing one.

"""

class ProductRecommender(BaseModel):
    recom_response: list[dict[str,str|int|float]|None]|None= Field(
        default_factory = list,
        description= (
            "Select and return the number of products from the provided database products. "
            "The default is two selected products."
            "The returned value must correspond to the products rows from the available "
            "products and should be the products that best matches the user's needs and preferences. "
            "Do not invent a new product or combine information from multiple products."
        )
    )

    recom_reason: str|None = Field(
        default = None,
        description= (
            "Explain why the selected product is the best recommendation for the user. "
            "Base the reasoning on the user's requirements and the actual attributes of the "
            "selected product, such as price, category, brand, specifications, rating, or other "
            "relevant product data."
            "Proivde the reason for each product individually, if there is more that one product."
        )
    )

    confidence: float|None = Field(
        default=None,
        ge = 0.0,
        le=1.0,
        description=(
            "Confidence score between 0 and 1 indicating how strongly the available products "
            "data supports this recommendation."
            "Set a confidence score for each selected product if there are more than one."
        )
    )

def _product_search_text(product) -> str:
    """Convert a product row to stable, descriptive text for embedding."""
    if isinstance(product, BaseModel):
        product = product.model_dump()
    elif hasattr(product, "_mapping"):
        product = dict(product._mapping)

    if isinstance(product, dict):
        searchable_product = {
            str(key): value
            for key, value in product.items()
            if value is not None and value != "" and value != []
        }
        return json.dumps(
            searchable_product,
            default=str,
            ensure_ascii=False,
            sort_keys=True,
        )

    return str(product)


def _create_chroma_client():
    """Create an in-memory Chroma client without writing a database to disk."""
    try:
        import chromadb
    except ModuleNotFoundError as exc:
        if exc.name != "chromadb":
            raise

        raise ImportError(
            "semantic_search requires the 'chromadb' package. "
            "Install it in the project environment with: pip install chromadb"
        ) from exc

    return chromadb.Client()


def semantic_search(products, user_message: str, limit: int | None = None):
    """
    Rank product rows through an in-memory Chroma vector collection.

    The original product objects are returned unchanged, so the result remains
    compatible with ``product_recommendation`` and existing database rows.
    ``limit=None`` returns every product in relevance order.
    """
    if products is None:
        return []

    product_rows = list(products)
    if not product_rows:
        return []

    if not isinstance(user_message, str):
        raise TypeError("user_message must be a string")

    if limit is not None and (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or limit < 0
    ):
        raise ValueError("limit must be a non-negative integer or None")

    if limit == 0:
        return []

    if not user_message.strip():
        return product_rows[:limit]

    client = _create_chroma_client()
    product_texts = [
        _product_search_text(product)
        for product in product_rows
    ]
    product_embeddings = embedding_model.embed_documents(product_texts)
    query_embedding = embedding_model.embed_query(user_message.strip())

    collection_name = f"product-recommendations-{uuid4().hex}"
    collection = client.create_collection(
        name=collection_name,
        embedding_function=None,
    )
    product_ids = [
        f"product-{index}"
        for index in range(len(product_rows))
    ]

    try:
        collection.add(
            ids=product_ids,
            documents=product_texts,
            embeddings=product_embeddings,
        )
        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=(
                len(product_rows)
                if limit is None
                else min(limit, len(product_rows))
            ),
        )
    finally:
        client.delete_collection(name=collection_name)

    products_by_id = dict(zip(product_ids, product_rows))
    ranked_ids = search_results["ids"][0]

    return [
        products_by_id[product_id]
        for product_id in ranked_ids
    ]


def product_recommendation(products,user_message:str):
    products = semantic_search(products, user_message)

    results = model.with_structured_output(ProductRecommender).invoke(
        [
            {
                "role":"system",
                "content":recommendation_model_prompt,
            },
            {
                "role":"user",
                "content":f"""
                User request:
                {user_message}

                Products list:
                {products}
                """
            }
        ]
    )
    return results



# user_input = input("What are you looking for ?: ")
# search_filters = extract_filters(
#     user_input,
# )
# filters_list = normalize_filters(search_filters)

# products_list = product_search(
#     category=filters_list.category,
#     color=filters_list.color,
#     size=filters_list.size,
#     brand=filters_list.brand,
#     min_price=filters_list.min_price,
#     max_price=filters_list.max_price,
#     limit=search_filters.limit,
# )
# recommendation = product_recommendation(products_list,user_input)


# print("--PRODUCTS LIST--")
# counter = 0

# for p in products_list:
#     counter += 1
#     print(p)

# print()
# print(f"ITEMS COUNTER:{counter}")
# print("------------------")
# print("--SEARCH FILTERS--")
# print(f"{search_filters}")
# print("------------------")
# counter = 0
# print("--RECOMMENDATIONS LIST--")

# if recommendation:
    
#     for r in list(recommendation.recom_response):
#         counter += 1
#         print(r)
# else:
#     print("No such product")
# print()
# print(f"REASON: {recommendation.recom_reason}")
# print("------------------")