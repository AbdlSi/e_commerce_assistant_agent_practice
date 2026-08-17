from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

from langchain_openai import ChatOpenAI
from langchain.tools import tool

from dotenv import load_dotenv

from database.models import engine
from sqlalchemy import text
import json

from product_search import ProductFilter ,extract_filters , normalize_filters,product_search

load_dotenv()

model = ChatOpenAI(
    model = "gpt-4.1-mini",
    temperature=0,
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

def product_recommendation(products,user_message:str):
    
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