# Marketplace Features - Reviews, Messages, Promo Codes, Wishlists, Refunds
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, update
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from database import (
    get_db, User, Product, Order, Vendor,
    ProductReview, VendorReview, ProductQuestion,
    Message, PromoCode, RefundRequest, Wishlist
)
from auth import get_current_user
import uuid

marketplace_router = APIRouter()

# ============ PYDANTIC MODELS ============

class ProductReviewCreate(BaseModel):
    product_id: int
    order_id: Optional[int] = None
    rating: int  # 1-5
    title: Optional[str] = None
    comment: Optional[str] = None
    images: Optional[List[str]] = []

class VendorReviewCreate(BaseModel):
    vendor_id: int
    order_id: Optional[int] = None
    rating: int
    comment: Optional[str] = None
    communication_rating: Optional[int] = None
    shipping_rating: Optional[int] = None
    product_quality_rating: Optional[int] = None

class ProductQuestionCreate(BaseModel):
    product_id: int
    question: str

class QuestionAnswerCreate(BaseModel):
    answer: str

class MessageCreate(BaseModel):
    receiver_id: int
    message: str
    order_id: Optional[int] = None
    product_id: Optional[int] = None
    attachments: Optional[List[str]] = []

class PromoCodeValidate(BaseModel):
    code: str
    order_total: float

class RefundRequestCreate(BaseModel):
    order_id: int
    reason: str
    description: Optional[str] = None
    images: Optional[List[str]] = []
    items: List[dict]  # [{product_id, quantity}]

class WishlistToggle(BaseModel):
    product_id: int

# ============ PRODUCT REVIEWS ============

@marketplace_router.post("/reviews/product")
async def create_product_review(
    review: ProductReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a product review"""
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Check if product exists
    result = await db.execute(select(Product).where(Product.id == review.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user already reviewed this product
    existing = await db.execute(
        select(ProductReview).where(
            ProductReview.product_id == review.product_id,
            ProductReview.user_id == current_user.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    # Check if verified purchase
    verified = False
    if review.order_id:
        order_result = await db.execute(
            select(Order).where(
                Order.id == review.order_id,
                Order.user_id == current_user.id
            )
        )
        order = order_result.scalar_one_or_none()
        if order:
            # Check if product was in this order
            for item in order.items:
                if item.get('id') == review.product_id or item.get('productId') == review.product_id:
                    verified = True
                    break
    
    new_review = ProductReview(
        product_id=review.product_id,
        user_id=current_user.id,
        order_id=review.order_id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        images=review.images or [],
        verified_purchase=verified
    )
    db.add(new_review)
    
    # Update product rating
    result = await db.execute(
        select(func.avg(ProductReview.rating), func.count(ProductReview.id))
        .where(ProductReview.product_id == review.product_id)
    )
    avg_rating, review_count = result.first()
    
    product.rating = round(float(avg_rating or review.rating), 1)
    product.reviews = int(review_count or 0) + 1
    
    await db.flush()
    
    return {
        "success": True,
        "message": "Review submitted successfully",
        "review": {
            "id": new_review.id,
            "rating": new_review.rating,
            "verified_purchase": verified
        }
    }

@marketplace_router.get("/reviews/product/{product_id}")
async def get_product_reviews(
    product_id: int,
    page: int = 1,
    limit: int = 10,
    sort: str = "recent",  # recent, helpful, highest, lowest
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for a product"""
    query = select(ProductReview).where(
        ProductReview.product_id == product_id,
        ProductReview.status == "approved"
    )
    
    if sort == "helpful":
        query = query.order_by(ProductReview.helpful_count.desc())
    elif sort == "highest":
        query = query.order_by(ProductReview.rating.desc())
    elif sort == "lowest":
        query = query.order_by(ProductReview.rating.asc())
    else:
        query = query.order_by(ProductReview.created_at.desc())
    
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    # Get rating distribution
    dist_result = await db.execute(
        select(ProductReview.rating, func.count(ProductReview.id))
        .where(ProductReview.product_id == product_id)
        .group_by(ProductReview.rating)
    )
    distribution = {str(i): 0 for i in range(1, 6)}
    for rating, count in dist_result.fetchall():
        distribution[str(rating)] = count
    
    # Get user info for each review
    reviews_data = []
    for rev in reviews:
        user_result = await db.execute(select(User).where(User.id == rev.user_id))
        user = user_result.scalar_one_or_none()
        reviews_data.append({
            "id": rev.id,
            "rating": rev.rating,
            "title": rev.title,
            "comment": rev.comment,
            "images": rev.images,
            "helpful_count": rev.helpful_count,
            "verified_purchase": rev.verified_purchase,
            "created_at": rev.created_at.isoformat(),
            "user": {
                "name": user.name if user else "Anonymous",
                "avatar": user.avatar if user else None
            }
        })
    
    return {
        "success": True,
        "reviews": reviews_data,
        "distribution": distribution,
        "page": page,
        "limit": limit
    }

@marketplace_router.post("/reviews/product/{review_id}/helpful")
async def mark_review_helpful(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a review as helpful"""
    result = await db.execute(select(ProductReview).where(ProductReview.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review.helpful_count += 1
    await db.flush()
    
    return {"success": True, "helpful_count": review.helpful_count}

# ============ VENDOR REVIEWS ============

@marketplace_router.post("/reviews/vendor")
async def create_vendor_review(
    review: VendorReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a vendor/seller review"""
    result = await db.execute(select(Vendor).where(Vendor.id == review.vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    new_review = VendorReview(
        vendor_id=review.vendor_id,
        user_id=current_user.id,
        order_id=review.order_id,
        rating=review.rating,
        comment=review.comment,
        communication_rating=review.communication_rating,
        shipping_rating=review.shipping_rating,
        product_quality_rating=review.product_quality_rating
    )
    db.add(new_review)
    
    # Update vendor rating
    result = await db.execute(
        select(func.avg(VendorReview.rating))
        .where(VendorReview.vendor_id == review.vendor_id)
    )
    avg_rating = result.scalar()
    vendor.rating = round(float(avg_rating or review.rating), 1)
    
    await db.flush()
    
    return {"success": True, "message": "Vendor review submitted"}

@marketplace_router.get("/reviews/vendor/{vendor_id}")
async def get_vendor_reviews(
    vendor_id: int,
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for a vendor"""
    result = await db.execute(
        select(VendorReview)
        .where(VendorReview.vendor_id == vendor_id)
        .order_by(VendorReview.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    reviews = result.scalars().all()
    
    reviews_data = []
    for rev in reviews:
        user_result = await db.execute(select(User).where(User.id == rev.user_id))
        user = user_result.scalar_one_or_none()
        reviews_data.append({
            "id": rev.id,
            "rating": rev.rating,
            "comment": rev.comment,
            "communication_rating": rev.communication_rating,
            "shipping_rating": rev.shipping_rating,
            "product_quality_rating": rev.product_quality_rating,
            "created_at": rev.created_at.isoformat(),
            "user": {
                "name": user.name if user else "Anonymous"
            }
        })
    
    return {"success": True, "reviews": reviews_data}

# ============ PRODUCT Q&A ============

@marketplace_router.post("/questions")
async def create_question(
    question: ProductQuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ask a question about a product"""
    result = await db.execute(select(Product).where(Product.id == question.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_question = ProductQuestion(
        product_id=question.product_id,
        user_id=current_user.id,
        question=question.question
    )
    db.add(new_question)
    await db.flush()
    
    return {"success": True, "message": "Question submitted", "question_id": new_question.id}

@marketplace_router.get("/questions/product/{product_id}")
async def get_product_questions(
    product_id: int,
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get Q&A for a product"""
    result = await db.execute(
        select(ProductQuestion)
        .where(ProductQuestion.product_id == product_id)
        .order_by(ProductQuestion.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    questions = result.scalars().all()
    
    questions_data = []
    for q in questions:
        user_result = await db.execute(select(User).where(User.id == q.user_id))
        user = user_result.scalar_one_or_none()
        questions_data.append({
            "id": q.id,
            "question": q.question,
            "answer": q.answer,
            "answered_at": q.answered_at.isoformat() if q.answered_at else None,
            "helpful_count": q.helpful_count,
            "status": q.status,
            "created_at": q.created_at.isoformat(),
            "user": {
                "name": user.name if user else "Anonymous"
            }
        })
    
    return {"success": True, "questions": questions_data}

@marketplace_router.post("/questions/{question_id}/answer")
async def answer_question(
    question_id: int,
    answer_data: QuestionAnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Answer a product question (vendor or admin)"""
    result = await db.execute(select(ProductQuestion).where(ProductQuestion.id == question_id))
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if user is vendor of this product or admin
    product_result = await db.execute(select(Product).where(Product.id == question.product_id))
    product = product_result.scalar_one_or_none()
    
    vendor_result = await db.execute(select(Vendor).where(Vendor.id == product.vendor_id))
    vendor = vendor_result.scalar_one_or_none()
    
    is_vendor = vendor and vendor.email == current_user.email
    is_admin = current_user.role == "admin"
    
    if not (is_vendor or is_admin):
        raise HTTPException(status_code=403, detail="Only the vendor or admin can answer")
    
    question.answer = answer_data.answer
    question.answered_by = current_user.id
    question.answered_at = datetime.utcnow()
    question.status = "answered"
    
    await db.flush()
    
    return {"success": True, "message": "Answer submitted"}

# ============ MESSAGING ============

@marketplace_router.post("/messages")
async def send_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message to another user"""
    # Generate conversation ID
    user_ids = sorted([current_user.id, message_data.receiver_id])
    conversation_id = f"conv_{user_ids[0]}_{user_ids[1]}"
    
    if message_data.order_id:
        conversation_id += f"_order_{message_data.order_id}"
    
    new_message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        order_id=message_data.order_id,
        product_id=message_data.product_id,
        message=message_data.message,
        attachments=message_data.attachments or []
    )
    db.add(new_message)
    await db.flush()
    
    return {
        "success": True,
        "message_id": new_message.id,
        "conversation_id": conversation_id
    }

@marketplace_router.get("/messages")
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conversations for current user"""
    result = await db.execute(
        select(Message)
        .where(or_(
            Message.sender_id == current_user.id,
            Message.receiver_id == current_user.id
        ))
        .order_by(Message.created_at.desc())
    )
    messages = result.scalars().all()
    
    # Group by conversation
    conversations = {}
    for msg in messages:
        if msg.conversation_id not in conversations:
            # Get other user
            other_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
            user_result = await db.execute(select(User).where(User.id == other_id))
            other_user = user_result.scalar_one_or_none()
            
            # Count unread
            unread_result = await db.execute(
                select(func.count(Message.id))
                .where(
                    Message.conversation_id == msg.conversation_id,
                    Message.receiver_id == current_user.id,
                    Message.read == False
                )
            )
            unread = unread_result.scalar()
            
            conversations[msg.conversation_id] = {
                "conversation_id": msg.conversation_id,
                "other_user": {
                    "id": other_user.id if other_user else None,
                    "name": other_user.name if other_user else "Unknown",
                    "avatar": other_user.avatar if other_user else None
                },
                "last_message": msg.message[:50] + "..." if len(msg.message) > 50 else msg.message,
                "last_message_at": msg.created_at.isoformat(),
                "unread_count": unread,
                "order_id": msg.order_id
            }
    
    return {"success": True, "conversations": list(conversations.values())}

@marketplace_router.get("/messages/{conversation_id}")
async def get_conversation_messages(
    conversation_id: str,
    page: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages in a conversation"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    messages = result.scalars().all()
    
    # Mark as read
    await db.execute(
        update(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.receiver_id == current_user.id,
            Message.read == False
        )
        .values(read=True, read_at=datetime.utcnow())
    )
    
    messages_data = []
    for msg in messages:
        sender_result = await db.execute(select(User).where(User.id == msg.sender_id))
        sender = sender_result.scalar_one_or_none()
        messages_data.append({
            "id": msg.id,
            "message": msg.message,
            "attachments": msg.attachments,
            "sender": {
                "id": sender.id if sender else None,
                "name": sender.name if sender else "Unknown",
                "avatar": sender.avatar if sender else None
            },
            "is_mine": msg.sender_id == current_user.id,
            "read": msg.read,
            "created_at": msg.created_at.isoformat()
        })
    
    return {"success": True, "messages": messages_data}

# ============ PROMO CODES ============

@marketplace_router.post("/promo/validate")
async def validate_promo_code(
    promo: PromoCodeValidate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate and apply a promo code"""
    result = await db.execute(
        select(PromoCode).where(
            PromoCode.code == promo.code.upper(),
            PromoCode.is_active == True
        )
    )
    code = result.scalar_one_or_none()
    
    if not code:
        raise HTTPException(status_code=404, detail="Invalid promo code")
    
    # Check validity
    now = datetime.utcnow()
    if code.valid_from and code.valid_from > now:
        raise HTTPException(status_code=400, detail="This code is not yet active")
    
    if code.valid_until and code.valid_until < now:
        raise HTTPException(status_code=400, detail="This code has expired")
    
    if code.usage_limit and code.times_used >= code.usage_limit:
        raise HTTPException(status_code=400, detail="This code has reached its usage limit")
    
    if promo.order_total < code.min_order_amount:
        raise HTTPException(
            status_code=400, 
            detail=f"Minimum order amount is £{code.min_order_amount:.2f}"
        )
    
    # Calculate discount
    if code.discount_type == "percentage":
        discount = promo.order_total * (code.discount_value / 100)
        if code.max_discount:
            discount = min(discount, code.max_discount)
    else:
        discount = code.discount_value
    
    return {
        "success": True,
        "code": code.code,
        "discount_type": code.discount_type,
        "discount_value": code.discount_value,
        "discount_amount": round(discount, 2),
        "new_total": round(promo.order_total - discount, 2)
    }

@marketplace_router.post("/promo/apply")
async def apply_promo_code(
    promo: PromoCodeValidate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply promo code (increment usage)"""
    result = await db.execute(
        select(PromoCode).where(PromoCode.code == promo.code.upper())
    )
    code = result.scalar_one_or_none()
    
    if code:
        code.times_used += 1
        await db.flush()
    
    return {"success": True}

# ============ REFUNDS ============

@marketplace_router.post("/refunds")
async def create_refund_request(
    refund: RefundRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a refund/return request"""
    # Check if order exists and belongs to user
    result = await db.execute(
        select(Order).where(
            Order.id == refund.order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status == "refunded":
        raise HTTPException(status_code=400, detail="This order has already been refunded")
    
    # Calculate refund amount based on items
    refund_amount = 0
    for item in refund.items:
        for order_item in order.items:
            if order_item.get('id') == item.get('product_id'):
                refund_amount += order_item.get('price', 0) * item.get('quantity', 1)
                break
    
    new_refund = RefundRequest(
        order_id=refund.order_id,
        user_id=current_user.id,
        reason=refund.reason,
        description=refund.description,
        images=refund.images or [],
        items=refund.items,
        refund_amount=refund_amount
    )
    db.add(new_refund)
    await db.flush()
    
    return {
        "success": True,
        "message": "Refund request submitted",
        "refund_id": new_refund.id,
        "refund_amount": refund_amount
    }

@marketplace_router.get("/refunds")
async def get_my_refund_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's refund requests"""
    result = await db.execute(
        select(RefundRequest)
        .where(RefundRequest.user_id == current_user.id)
        .order_by(RefundRequest.created_at.desc())
    )
    refunds = result.scalars().all()
    
    return {
        "success": True,
        "refunds": [{
            "id": r.id,
            "order_id": r.order_id,
            "reason": r.reason,
            "description": r.description,
            "refund_amount": r.refund_amount,
            "status": r.status,
            "created_at": r.created_at.isoformat()
        } for r in refunds]
    }

# ============ WISHLIST ============

@marketplace_router.post("/wishlist/toggle")
async def toggle_wishlist(
    item: WishlistToggle,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add/remove item from wishlist"""
    # Check if already in wishlist
    result = await db.execute(
        select(Wishlist).where(
            Wishlist.user_id == current_user.id,
            Wishlist.product_id == item.product_id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        await db.delete(existing)
        await db.flush()
        return {"success": True, "action": "removed", "in_wishlist": False}
    else:
        new_item = Wishlist(
            user_id=current_user.id,
            product_id=item.product_id
        )
        db.add(new_item)
        await db.flush()
        return {"success": True, "action": "added", "in_wishlist": True}

@marketplace_router.get("/wishlist")
async def get_wishlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's wishlist"""
    result = await db.execute(
        select(Wishlist)
        .where(Wishlist.user_id == current_user.id)
        .order_by(Wishlist.created_at.desc())
    )
    wishlist_items = result.scalars().all()
    
    items = []
    for w in wishlist_items:
        product_result = await db.execute(select(Product).where(Product.id == w.product_id))
        product = product_result.scalar_one_or_none()
        if product:
            items.append({
                "id": w.id,
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "original_price": product.original_price,
                "image": product.image,
                "in_stock": product.in_stock,
                "rating": product.rating,
                "added_at": w.created_at.isoformat()
            })
    
    return {"success": True, "items": items, "count": len(items)}

@marketplace_router.get("/wishlist/check/{product_id}")
async def check_wishlist(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if product is in wishlist"""
    result = await db.execute(
        select(Wishlist).where(
            Wishlist.user_id == current_user.id,
            Wishlist.product_id == product_id
        )
    )
    existing = result.scalar_one_or_none()
    
    return {"in_wishlist": existing is not None}

# ============ ORDER TRACKING ============

@marketplace_router.get("/orders/tracking/{order_id}")
async def get_order_tracking(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get order tracking information"""
    result = await db.execute(
        select(Order).where(Order.order_id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Build tracking timeline
    timeline = [
        {
            "status": "order_placed",
            "title": "Order Placed",
            "description": "Your order has been received",
            "completed": True,
            "date": order.created_at.isoformat()
        }
    ]
    
    statuses = ["processing", "shipped", "in_transit", "out_for_delivery", "delivered"]
    status_titles = {
        "processing": ("Processing", "Your order is being prepared"),
        "shipped": ("Shipped", "Your order has been shipped"),
        "in_transit": ("In Transit", "Your order is on its way"),
        "out_for_delivery": ("Out for Delivery", "Your order will arrive today"),
        "delivered": ("Delivered", "Your order has been delivered")
    }
    
    current_index = statuses.index(order.delivery_status) if order.delivery_status in statuses else -1
    
    for i, status in enumerate(statuses):
        title, desc = status_titles[status]
        timeline.append({
            "status": status,
            "title": title,
            "description": desc,
            "completed": i <= current_index,
            "date": order.delivered_at.isoformat() if status == "delivered" and order.delivered_at else None
        })
    
    return {
        "success": True,
        "order_id": order.order_id,
        "status": order.status,
        "delivery_status": order.delivery_status,
        "tracking_number": order.tracking_number,
        "carrier": order.carrier,
        "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
        "timeline": timeline
    }

@marketplace_router.get("/orders/history")
async def get_order_history(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's order history"""
    query = select(Order).where(Order.user_id == current_user.id)
    
    if status:
        query = query.where(Order.status == status)
    
    query = query.order_by(Order.created_at.desc()).offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Order.id)).where(Order.user_id == current_user.id)
    )
    total = count_result.scalar()
    
    orders_data = []
    for order in orders:
        orders_data.append({
            "id": order.id,
            "order_id": order.order_id,
            "items": order.items,
            "total": order.total,
            "status": order.status,
            "delivery_status": order.delivery_status,
            "tracking_number": order.tracking_number,
            "created_at": order.created_at.isoformat(),
            "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None
        })
    
    return {
        "success": True,
        "orders": orders_data,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }
