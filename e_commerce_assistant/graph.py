from typing import Literal, Annotated
from typing_extensions import TypedDict
import os 
import requests

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.messages import AnyMessage, HumanMessage

from e_commerce_assistant.tools.product_search_recommendation import extract_filters, normalize_filters,product_search, ProductFilter
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
    search_result:dict[str,str|int|float]
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
product_searcher_prompt ="""

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
    result = product_search(filters)
    return {
        "search_result":result,
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
                You are an e-commerce assistant.
                Answer using only the provided search results.
                Do not invent product information.
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

def decide_next_node(state:AgentState)->str:
    if state["intent"] == "product_search":
        return "extract_product_filters"
    # elif state["intent"] == "product_recommendation":
    #     return "product_recommendation"
    # elif state["intent"] == "order_status":
    #     return "order_status"
    # elif state["intent"] == "faq":
    #     return "faq"
    # elif state["intent"] == "greeting":
    #     return "greeting"
    
graph.add_node("intent_classification",classify_intent)

graph.add_node("extract_product_filters",extract_product_filters)
graph.add_node("normalize_product_filters",normalize_product_filters)
graph.add_node("product_search",searching_products)
graph.add_node("generate_search_response",generate_search_response)

# graph.add_node("product_recommendation",product_recommendation)
# graph.add_node("order_status",order_status)
# graph.add_node("faq",faq)
# graph.add_node("greeting",greeting)
graph.add_node("router",lambda state:state)

graph.add_edge(START,"intent_classification")
graph.add_edge("intent_classification","router")
graph.add_conditional_edges(
    "router",
    decide_next_node,
    {
        "extract_product_filters":"extract_product_filters",
        # "product_recommendation":"product_recommendation",
        # "order_status":"order_status",
        # "faq":"faq",
        # "greeting":"greeting",
    }
    )

graph.add_edge("extract_product_filters","normalize_product_filters")
graph.add_edge("normalize_product_filters","product_search")
graph.add_edge("product_search","generate_search_response")
graph.add_edge("generate_search_response",END)

# graph.add_edge("product_recommendation",END)

# graph.add_edge("order_status",END)

# graph.add_edge("faq",END)

# graph.add_edge("greeting",END)

app= graph.compile()
user_input = input("Write something: ")
final_input = {
    "user_message":user_input
}
result = app.invoke(final_input)

print(result["response"])
