import stripe
import os
from fastapi import HTTPException

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class StripePayment:
    @staticmethod
    async def create_payment_intent(amount: float, currency: str = 'gbp', metadata: dict = None):
        """Create a Stripe payment intent"""
        try:
            # Convert to smallest currency unit (pence for GBP)
            amount_in_pence = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_in_pence,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True},
            )
            
            return {
                'clientSecret': intent.client_secret,
                'paymentIntentId': intent.id
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    async def confirm_payment(payment_intent_id: str):
        """Confirm a payment intent"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'status': intent.status,
                'amount': intent.amount / 100,  # Convert back to pounds
                'id': intent.id
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    async def create_customer(email: str, name: str):
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            return customer.id
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def process_apple_pay(payment_method_id: str, amount: float):
        """Process Apple Pay payment through Stripe"""
        try:
            amount_in_pence = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_in_pence,
                currency='gbp',
                payment_method=payment_method_id,
                confirm=True,
                automatic_payment_methods={'enabled': True, 'allow_redirects': 'never'},
            )
            
            return {
                'status': intent.status,
                'paymentIntentId': intent.id,
                'amount': intent.amount / 100
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))