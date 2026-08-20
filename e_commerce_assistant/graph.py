from typing import Literal, Annotated
from typing_extensions import TypedDict
import os 
import requests

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.messages import AnyMessage, HumanMessage

from e_commerce_assistant.tools.product_search import extract_filters, normalize_filters,product_search, ProductFilter
from e_commerce_assistant.tools.product_recommendation import product_recommendation, ProductRecommender,semantic_search
from e_commerce_assistant.tools.order_status import extract_order_id, order_search, order_search_response_prompt
from e_commerce_assistant.tools.faq import faqs_db, faq_response_prompt

load_dotenv()

Intent = Literal[
    "product_search",
    "product_recommendation",
    "order_status",
    "faq",
    "greeting",
    "unsupported",         
    ]

class AgentState(TypedDict, total = False):
    user_message:str
    intent:Intent
    confidence:float
    classification_reason:str
    product_filters:ProductFilter
    search_result:list[dict[str,str|int|float]]
    recommendation_result:list[dict[str,str|int|float]]
    recommendation_reason: str
    orders_id: int
    order_search_result:list[dict[str,str|int|float]]
    faq_result:dict[str,str|int|float]
    message: Annotated[list[AnyMessage],add_messages]
    response:str


graph = StateGraph(AgentState)

class IntentClassification(BaseModel):
    intent:Intent

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confience score between 0 and 1",

    )

    reason: str = Field(
        description="A brief explanation for the classification"
    )

class ProductSearch(BaseModel):
    found_products: str = Field(
        description="A response for the client's request to search for specific products"
    )

model = ChatOpenAI(
    model = "gpt-4.1-mini",
    temperature=0,
    )

classifier_prompt ="""
You are an intent classifier for an e-commerce customer-support chatbot.

Classify the user's message into exactly one of these intents:

1. product_search
   The user provides specific product requirements and wants matching products.
   Example: "Show me black running shoes under $100."

2. product_recommendation
   The user wants advice deciding which product would suit them.
   Example: "Which laptop is best for a computer science student?"

3. order_status
   The user asks about an existing order, shipment, delivery, or tracking.
   Example: "Where is order 4821?"

4. faq
   The user asks about store policies or general company information.
   Example: "What is your return policy?"

5. greeting
   The user greets the chatbot without making another request.
   Example: "Hello."

6. unsupported
   The message is unclear or outside the supported e-commerce tasks.

Important rules:
- Return only one intent.
- Use product_search when the user already knows relevant requirements.
- Use product_recommendation when the user needs help choosing.
- Do not invent a new intent.
- Assign a realistic confidence score.
""" 


def classify_intent(state:AgentState)->AgentState:
    message = state["user_message"]
    result = model.with_structured_output(IntentClassification).invoke(
        [
            {
                "role":"system",
                "content":classifier_prompt,
            },
            {
                "role":"user",
                "content":message
            },
        ]
    )

    return {
        "intent":result.intent,
        "confidence":result.confidence,
        "classification_reason":result.reason,
    }

def extract_product_filters(state:AgentState)->AgentState:
    filters = extract_filters(state["user_message"])
    return{
        "product_filters":filters
    }

def normalize_product_filters(state:AgentState)->AgentState:
    normalized = normalize_filters(state["product_filters"])
    return {
        "product_filters":normalized
    }

def searching_products(state:AgentState)->AgentState:
    filters = state["product_filters"]
    result = product_search(
        category=filters.category, 
        color =filters.color, 
        size = filters.size, 
        brand = filters.brand,
        min_price= filters.min_price,
        max_price= filters.max_price,
        limit = filters.limit,
    )
    return {
        "search_result":result,
    }

def recommending_products(state:AgentState)->AgentState:
    products = state["search_result"]
    user_message = state["user_message"]
    result = product_recommendation(products,user_message)
    return {
        "recommendation_result":result.recom_response,
        "recommendation_reason":result.recom_reason,
    }

def extracting_order_id(state:AgentState)->AgentState:
    user_message = state["user_message"]
    result = extract_order_id(user_message)
    return {
        "orders_id":result
    }

def searching_order(state:AgentState)->AgentState:
    order_id = state["orders_id"]
    result = order_search(order_id)
    return {
        "order_search_result":result
    }
    
def generate_search_response(state:AgentState)->AgentState:
    human_message= HumanMessage(
        content=state["user_message"]
    )
    response = model.invoke(
        [
            {
                "role":"system",
                "content":"""
                You are the final response generator for an e-commerce product search system.

                Your task is to present the provided product search results in a clear, useful, and natural way that directly answers the user's request.

                ## Instructions

                1. Use only the provided product search results.
                2. Do not invent, modify, or assume any product information.
                3. Do not introduce products that are not present in the search results.
                4. Present the products that are most relevant to the user's request.
                5. Preserve important product details such as:

                * product name
                * brand
                * price
                * category
                * color
                * size
                * rating
                * relevant features
                6. Prioritize details that are relevant to the user's request rather than listing every available database field.
                7. If multiple products are returned, present them in a way that makes them easy to compare.
                8. Do not choose a single "best" product unless the user explicitly asks for a recommendation.
                9. Do not perform new filtering or change the search criteria. Treat the provided search results as the authoritative results of the search operation.
                10. If the results only partially satisfy the user's request, clearly mention the limitation.
                11. If no products are returned, tell the user that no matching products were found.
                12. Do not expose internal database fields or implementation details unless they are useful to the user.
                13. Do not mention internal concepts such as database queries, search nodes, state, filters, SQL, or tool execution.
                14. Keep the answer concise, conversational, and easy to scan.
                15. Do not claim that a product has a feature unless that feature is explicitly present in the provided data.

                Your purpose is to **present search results**, not to make a product recommendation.

                Use the user's original request to determine which details are most useful to mention.

                """
            },
            {
                "role":"user",
                "content":f"""
                User request:
                {state["user_message"]}

                Product search results:
                {state["search_result"]}
                """
            }
        ]
    )
    return {
        "message":[
            human_message,
            response
        ],
        "response":response.content
    }

def generate_recommendation_response(state:AgentState)->AgentState:
    human_message = HumanMessage(
        content=state["user_message"]
    )
    response = model.invoke(
        [
            {   
                "role":"system",
                "content":"""
                You are the final response generator for an e-commerce product recommendation system.

                Your task is to generate a clear, helpful, and concise response to the user based only on the recommendation data provided to you.

                ## Instructions

                1. Use only the provided recommendation data and product information.
                2. Do not invent, assume, or modify any product details.
                3. Do not recommend a different product.
                4. Clearly state which product is recommended.
                5. Briefly explain why the product matches the user's request.
                6. Mention the strongest relevant factors, such as:
                * price
                * brand
                * category
                * rating
                * features
                * size
                * color
                * intended use
                7. If there are unmet user preferences, mention them clearly and naturally.
                8. Do not claim that the product perfectly matches the user if the recommendation data says otherwise.
                9. Keep the response conversational and easy to understand.
                10. Avoid unnecessary technical details, database terminology, internal reasoning, confidence calculations, or references to the recommendation system.
                11. Do not mention that the product came from a database or search result unless that is useful to the user.
                12. Do not expose internal fields such as `product_id`, `matched_preferences`, `unmet_preferences`, or `confidence` directly. Use them only to construct the answer.
                13. If no valid product was selected, explain that there is not enough suitable product information to make a recommendation rather than inventing one.
                14. Use the provided recommendation reason to generate a better response for the user.
                The final answer should directly answer the user's product request and explain the recommendation using only the supplied information.
    
                """
            },
            {
                "role":"user",
                "content":f"""
                User request:
                {state["user_message"]}

                Product recommendation results:
                {state["recommendation_result"]}

                Product recommendation reason:
                {state['classification_reason']}
                
                """
            },
        ]
    )
    return {
        "message":[
            human_message,
            response,
        ],
        "response":response.content
    }

def generate_order_search_response(state:AgentState)->AgentState:
    human_message = HumanMessage(
        content=state["user_message"]
    )
    response = model.invoke(
        [
            {
                "role":"system",
                "content":order_search_response_prompt

            },
            {
                "role":"user",
                "content":f"""
                User request:
                {state["user_message"]}

                orders search results:
                {state['order_search_result']}
                """
            }
        ]
    )   
    return {
        "message":[
            human_message,
            response
        ],
        "response":response.content
    }

def extract_faq(state:AgentState)->AgentState:
    user_message = state["user_message"]
    result = semantic_search(faqs_db,user_message,limit=1)
    return {
        "faq_result":result[0]
    }

def generate_faq_response(state:AgentState)->AgentState:
    human_message = HumanMessage(
        content=state["user_message"]
    )
    response = model.invoke(
        [
            {
                "role":"system",
                "content":faq_response_prompt
            },
            {
                "role":"user",
                "content":f"""
                User request:
                {state["user_message"]}

                Retrieved FAQ question:
                {state['faq_result']['question']}

                Retrieved FAQ answer:
                {state['faq_result']["answer"]}
                """
            }
        ]
    )
    return {
        "message":[
            human_message,
            response
        ],
        "response":response.content
    }

def decide_next_node(state:AgentState)->str:
    if state["intent"] == "product_search" or state["intent"] == "product_recommendation":
        return "extract_product_filters"

    elif state["intent"] == "order_status":
        return "extracting_order_id"
    
    elif state["intent"] == "faq":
        return "extract_faq"
    
    # elif state["intent"] == "greeting":
    #     return "greeting"

def decide_search_recommend_node(state:AgentState)->str:
    if state["intent"] == "product_search":
        return "generate_search_response"
    
    elif state["intent"] == "product_recommendation":
        return "product_recommendation"  
    
graph.add_node("intent_classification",classify_intent)

graph.add_node("extract_product_filters",extract_product_filters)
graph.add_node("normalize_product_filters",normalize_product_filters)
graph.add_node("product_search",searching_products)
graph.add_node("generate_search_response",generate_search_response)

graph.add_node("product_recommendation",recommending_products)
graph.add_node("generate_recommendation_response", generate_recommendation_response)

graph.add_node("extracting_order_id",extracting_order_id)
graph.add_node("searching_order",searching_order)
graph.add_node("generate_order_search_response",generate_order_search_response)

graph.add_node("extract_faq",extract_faq)
graph.add_node("generate_faq_response",generate_faq_response)

# graph.add_node("greeting",greeting)
graph.add_node("router",lambda state:state)

graph.add_edge(START,"intent_classification")
graph.add_edge("intent_classification","router")
graph.add_conditional_edges(
    "router",
    decide_next_node,
    {
        "extract_product_filters":"extract_product_filters",
        "extracting_order_id":"extracting_order_id",
        "extract_faq":"extract_faq",
        # "greeting":"greeting",
    }
    )

graph.add_edge("extract_product_filters","normalize_product_filters")
graph.add_edge("normalize_product_filters","product_search")
graph.add_conditional_edges(
    "product_search",
    decide_search_recommend_node,
    {
        "generate_search_response":"generate_search_response",
        "product_recommendation":"product_recommendation",
    }
)
graph.add_edge("product_recommendation","generate_recommendation_response")
graph.add_edge("generate_search_response",END)
graph.add_edge("generate_recommendation_response",END)


graph.add_edge("extracting_order_id","searching_order")
graph.add_edge("searching_order","generate_order_search_response")
graph.add_edge("generate_order_search_response",END)

graph.add_edge("extract_faq","generate_faq_response")
graph.add_edge("generate_faq_response",END)

# graph.add_edge("greeting",END)

app= graph.compile()
user_input = input("Write something: ")
final_input = {
    "user_message":user_input
}
result = app.invoke(final_input)


print('SEARCH RESULTS:')
print(result["response"])
print(" ")
print("INTENT:")
print(result['intent'])
print(" ")
print('CONFIDENCE:')
print(result['confidence'])

