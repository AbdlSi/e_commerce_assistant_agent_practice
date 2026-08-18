from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

<<<<<<< HEAD
from langchain_openai import ChatOpenAI
=======
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
>>>>>>> f8db6a8 (new changes)
from langchain.tools import tool

from dotenv import load_dotenv

from database.models import engine
from sqlalchemy import text
import json

<<<<<<< HEAD
from product_search import ProductFilter ,extract_filters , normalize_filters,product_search

=======
>>>>>>> f8db6a8 (new changes)
load_dotenv()

model = ChatOpenAI(
    model = "gpt-4.1-mini",
    temperature=0,
)

<<<<<<< HEAD
=======
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

>>>>>>> f8db6a8 (new changes)
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

<<<<<<< HEAD
user_input = "Winter is coming, and I am looking for clothes that keep warm during the cold days"

search_filters = extract_filters(
    user_input,
)
filters_list = normalize_filters(search_filters)

products_list = product_search(    
    category=filters_list.category, 
    color =filters_list.color, 
    size = filters_list.size, 
    brand = filters_list.brand,
    min_price= filters_list.min_price,
    max_price= filters_list.max_price,
    limit = filters_list.limit,
    review_count=filters_list.review_count,
    rating=filters_list.rating,
 )



=======
>>>>>>> f8db6a8 (new changes)
class ProductRecommender(BaseModel):
    recom_response: list[dict[str,str|int|float]|None]|None = Field(
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

<<<<<<< HEAD
def product_recommendation(products,user_message:str):
    
=======

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
        return json.dumps(searchable_product, default=str, ensure_ascii=False, sort_keys=True)

    return str(product)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    """Calculate cosine similarity without requiring an additional dependency."""
    if len(left) != len(right):
        raise ValueError("Embedding vectors must have the same dimensions")

    dot_product = sum(a * b for a, b in zip(left, right))
    left_norm = sum(value * value for value in left) ** 0.5
    right_norm = sum(value * value for value in right) ** 0.5

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot_product / (left_norm * right_norm)


def semantic_search(products, user_message: str, limit: int | None = None):
    """
    Rank product rows by their semantic similarity to a user's request.

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
    if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 0):
        raise ValueError("limit must be a non-negative integer or None")
    if limit == 0:
        return []
    if not user_message.strip():
        return product_rows[:limit]

    product_texts = [_product_search_text(product) for product in product_rows]
    product_embeddings = embedding_model.embed_documents(product_texts)
    query_embedding = embedding_model.embed_query(user_message.strip())

    ranked_products = sorted(
        zip(product_rows, product_embeddings),
        key=lambda item: _cosine_similarity(query_embedding, item[1]),
        reverse=True,
    )
    ranked_rows = [product for product, _ in ranked_products]
    return ranked_rows[:limit]


def product_recommendation(products,user_message:str):
    products = semantic_search(products, user_message)

>>>>>>> f8db6a8 (new changes)
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


<<<<<<< HEAD
recommendation = product_recommendation(products_list,user_input)

print("--SEARCH FILTERS--")
print(f"{filters_list}")
print("------------------")
print("--PRODUCTS LIST--")
counter = 0 
for p in products_list:
    counter += 1
    print(p)
print( )
print(f"ITEMS COUNTER:{counter}")
print("------------------")
print("--RECOMMENDATIONS LIST--")
for r in recommendation.recom_response:
    print(r)
print( )
print(f"REASON: {recommendation.recom_reason}")
print("------------------")
=======
if __name__ == "__main__":
    from product_search import extract_filters, normalize_filters, product_search

    user_input = "Winter is coming, and I am looking for clothes that keep warm during the cold days"

    search_filters = extract_filters(
        user_input,
    )
    filters_list = normalize_filters(search_filters)

    products_list = product_search(
        category=filters_list.category,
        color=filters_list.color,
        size=filters_list.size,
        brand=filters_list.brand,
        min_price=filters_list.min_price,
        max_price=filters_list.max_price,
        limit=filters_list.limit,
    )

    recommendation = product_recommendation(products_list,user_input)

    print("--SEARCH FILTERS--")
    print(f"{filters_list}")
    print("------------------")
    print("--PRODUCTS LIST--")
    counter = 0
    for p in products_list:
        counter += 1
        print(p)
    print()
    print(f"ITEMS COUNTER:{counter}")
    print("------------------")
    print("--RECOMMENDATIONS LIST--")
    for r in recommendation.recom_response:
        print(r)
    print()
    print(f"REASON: {recommendation.recom_reason}")
    print("------------------")
>>>>>>> f8db6a8 (new changes)
