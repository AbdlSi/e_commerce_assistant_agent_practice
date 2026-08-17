from sqlalchemy import create_engine, String, Integer, URL, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, Session
from decimal import Decimal
import os 
from dotenv import load_dotenv

load_dotenv()

db_url =URL.create(
    drivername=os.getenv("DB_DRIVERNAME"),
    username = os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),  
    database=os.getenv("DB_NAME"), 
    host="localhost",
    port = 3306
)
engine = create_engine(db_url)
base = declarative_base()

class products(base):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(9), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    brand: Mapped[str|None] = mapped_column(String(25))
    description: Mapped[str|None] = mapped_column(String(300))
    gender: Mapped[str|None] = mapped_column(String(20))
    base_price: Mapped[Decimal] = mapped_column( Numeric(5,2), nullable=False, )
    rating: Mapped[Decimal|None] = mapped_column(Numeric(3,1))
    review_count : Mapped[int] = mapped_column(Integer , default=0 , nullable=False)
    active: Mapped[str] = mapped_column(String(5), nullable= False, default="TRUE")

class products_variants(base):
    __tablename__ = "products_variants"
    variant_product_id: Mapped[int] = mapped_column(Integer, autoincrement=True , primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id"),nullable=False)
    sku: Mapped[str] = mapped_column(String(20),nullable=False,unique=True)
    color: Mapped[str|None] =   (String(20))
    size: Mapped[str|None] = mapped_column(String(5))
    price: Mapped[Decimal|None] = mapped_column(Numeric(5,2))
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[str] = mapped_column(String(7), nullable= False)

