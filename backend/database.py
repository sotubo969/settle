from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import os

# SQLite for now (can easily switch to MySQL later)
# For MySQL: mysql+aiomysql://user:password@localhost/dbname
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///./afromarket.db')

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=True)
    role = Column(String(50), default='customer')
    avatar = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    apple_id = Column(String(255), unique=True, nullable=True)
    addresses = Column(JSON, default=list)
    payment_methods = Column(JSON, default=list)
    wishlist = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship('Order', back_populates='user')
    cart = relationship('Cart', back_populates='user', uselist=False)

class Vendor(Base):
    __tablename__ = 'vendors'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    business_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    postcode = Column(String(20), nullable=False)
    location = Column(String(100), nullable=False)
    verified = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    total_sales = Column(Integer, default=0)
    commission = Column(Float, default=1.0)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    products = relationship('Product', back_populates='vendor')

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    image = Column(String(500), nullable=False)
    images = Column(JSON, default=list)
    category = Column(String(100), nullable=False, index=True)
    category_id = Column(Integer, nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    vendor_info = Column(JSON, nullable=False)
    rating = Column(Float, default=0.0)
    reviews = Column(Integer, default=0)
    stock = Column(Integer, nullable=False)
    weight = Column(String(50), nullable=False)
    in_stock = Column(Boolean, default=True)
    featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    vendor = relationship('Vendor', back_populates='products')

class Cart(Base):
    __tablename__ = 'carts'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    items = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', back_populates='cart')

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    items = Column(JSON, nullable=False)
    shipping_info = Column(JSON, nullable=False)
    payment_info = Column(JSON, nullable=False)
    subtotal = Column(Float, nullable=False)
    delivery_fee = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String(50), default='pending')
    # Delivery tracking fields
    delivery_status = Column(String(50), default='processing')  # processing, shipped, in_transit, out_for_delivery, delivered
    tracking_number = Column(String(100), nullable=True)
    carrier = Column(String(100), nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', back_populates='orders')


class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # page_view, product_view, product_click, add_to_cart
    page_url = Column(String(500), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PageVisit(Base):
    __tablename__ = 'page_visits'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    page = Column(String(255), nullable=False)
    visits = Column(Integer, default=1)
    unique_visitors = Column(Integer, default=1)

# Database session dependency
async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        try:
            await session.close()
        except Exception:
            pass  # Ignore close errors if session is already closed

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)