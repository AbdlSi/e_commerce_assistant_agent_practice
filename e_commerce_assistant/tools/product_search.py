from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

from langchain_openai import ChatOpenAI
from langchain.tools import tool

from dotenv import load_dotenv

from database.models import engine
from sqlalchemy import text


load_dotenv()

model = ChatOpenAI(
    model = "gpt-4.1-mini",
    temperature=0,
)

class ProductFilter(BaseModel):
    client_request:str|None = Field(
        default=None,
        description=(
            "General product name, feature, or use case, "
            "such as waterproof hiking shoes."
        ),
    ) 

    color: str|None = Field(
        default=None,
        description=(
            "The color of the requested order. "
        ),
    )

    size: Literal["XS","S","M","L","XL"]|int|None = Field(
        default=None,
        description=(
            "The size of the requested order. "
        ),
    )

    category:Literal['shoes','jackets','t-shirts','jeans','bags','hoodies', 'dresses','watches','accessories']|None = Field(
        default=None,
        description=(
            "Product category, such as shoes or jackets. "
        ),
    )

    brand:str|None = Field(
        default=None,
        description=(
            "The brand of the requested order. "
        ),
    )

    min_price:float|None = Field(
        default=None,
        ge = 0,
        description="Minimun acceptable price. ",
    )

    max_price:float|None = Field(
        default=None,
        ge = 0,
        description="Maximum acceptable price. ",
    )

    features:list[str] = Field(
        default= list,
        description=(
            "Requested features such as lightweight, or waterproof"
            "sporty, or cotton."
        )
    )

    in_stock_only:bool = Field(
        default=True,
        description="The requested product should be available otherwise it should be excluded"
    )

    sort_by:Literal[
        "relevance",
        "price_high_to_low",
        "price_low_to_high",

    ]=Field(
        default="relevance",
        description=(
            "How product results should be ordered. "
            "Use price_low_to_high for cheapest-first requests, "
            "price_high_to_low for most-expensive-first requests, "
            "and relevance when no explicit sorting preference is given."
        )
    )

    limit:int = Field(
        default=5,
        ge=1,
        le=20,
    )

    description:str|None = Field(
        default=None,
        description="A natural-language description of the product, including its key characteristics, intended use, and notable features."
    )   

    name:str|None = Field(
        default=None,
        description="The official product name as stored in the product database."
    )

    review_count:int|None = Field(
        default=None,
        description="The total number of customer reviews submitted for the product."
    )

    rating:float|None = Field(
        default=None,
        ge = 1.0,
        le= 10.0,
        description="The product's average customer rating on a scale from 1.0 to 10.0, where higher values indicate better overall customer satisfaction. "
    )
    
    @model_validator(mode="after")
    def validate_prices(self):
        if(
            self.min_price is not None and self.max_price is not None and self.min_price > self.max_price
        ):
            raise ValueError("min_price cannot be greater than the max_price")

        return self



filter_extractor  = model.with_structured_output(
    ProductFilter,
)

filter_model_prompt = """
Rules:

- Do not invent filters that the customer did not provide.
- Use null for unknown single-value fields.
- Use an empty list when no features are mentioned.
- Put the main product type inside category when clear.
- Put a more general phrase inside query when useful.
- Interpret "under", "below", or "up to" as max_price.
- Interpret "over", "above", or "at least" as min_price.
- Use in_stock_only=True unless the customer explicitly asks to see
  unavailable products.
- Use price_low_to_high when the customer asks for cheapest products.
- Use price_high_to_low when the customer asks for most expensive products.
- Do not include currency symbols in numeric price fields.
- Interpret "M" as medium, "XS" as x-small or xsmall or x small, "S" as small, 
  "L" as large, "XL" as x-large or xlarge or x large.
- If user request his size in number such (42,43,etc...) then the size field 
  is an integer otherwise it is not.

"""
def extract_filters(user_message:str):
    result = model.with_structured_output(ProductFilter,).invoke(
        [
            {
                "role":"system",
                "content":filter_model_prompt
            },
            {
                "role":"user",
                "content":user_message
            },
        ]
    )
    return result

def normalize_filters(filters):
    if filters.color:
        filters.color = filters.color.strip().lower()

    if filters.brand:
        filters.brand = filters.brand.strip().capitalize()

    if filters.features:
        features_list = []
        for feature in filters.features:
            feature = feature.strip().capitalize()
            features_list.append(feature)
        filters.features = features_list

    return filters

def product_search(
    category:str|None=None,
    color:str|None=None,
    size:str|None=None,
    brand:str|None=None,
    min_price:float|None=None,
    max_price:float|None=None,
    limit:int|None= None,
<<<<<<< HEAD
=======
    rating:float|None = None,
>>>>>>> f8db6a8 (new changes)
):
    """
    Search products in the database using optional filters such as
    category, color, size, brand, minimum price, and maximum price.
    """
    query = """
        SELECT products.category , products.brand , products_variants.color , products_variants.size , products_variants.price
        FROM products
        JOIN products_variants
        ON products.product_id = products_variants.product_id
        WHERE 1=1
    """

    params = {}
    if category is not None:
        query += " AND products.category = :category"
        params["category"] = category

    if color is not None:
        query += " AND products_variants.color = :color"
        params["color"] = color

    if size is not None:
        query += " AND products_variants.size = :size"
        params["size"] = size

    if brand is not None:
        query += " AND products.brand = :brand"
        params["brand"] = brand

    if min_price is not None:
        query += " AND products_variants.price >= :min_price"
        params["min_price"] = min_price

    if max_price is not None:
        query += " AND products_variants.price <= :max_price"
        params["max_price"] = max_price

    if limit is not None:
        query += " LIMIT :limit"
        params["limit"] = limit

    with engine.connect() as conn:
        result = conn.execute(
            text(query),
            params
        )

        products_list = result.mappings().all()
    return [dict(product) for  product in products_list]

user_input = "I need a waterproof shoes with robber grip "
search_filters = extract_filters(
    user_input,
)
<<<<<<< HEAD
filters = normalize_filters(search_filters)

products_list = product_search(    
    category=filters.category, 
    color =filters.color, 
    size = filters.size, 
    brand = filters.brand,
    min_price= filters.min_price,
    max_price= filters.max_price,
    limit = filters.limit,
 )

counter = 0
print("--SEARCH FILTERS--")
print(f"{filters}")
print("------------------")
print("--PRODUCTS LIST--")
counter = 0 
for p in filters:
=======
filters_list = normalize_filters(search_filters)

products_list = product_search(    

    category=filters_list.category, 
    color =filters_list.color, 
    size = filters_list.size, 
    brand = filters_list.brand,
    min_price= filters_list.min_price,
    max_price= filters_list.max_price,
    limit = filters_list.limit,
    rating= filters_list.rating,
 )

counter = 0
print("--SEARCH FILTERS--")
print(f"{filters_list}")
print("------------------")
print("--PRODUCTS LIST--")
for p in products_list:
>>>>>>> f8db6a8 (new changes)
    counter += 1
    print(p)
print( )
print(f"ITEMS COUNTER:{counter}")
print("------------------")
