from paypalrestsdk import Payment as PayPalPayment, configure as paypal_configure
import os
from fastapi import HTTPException

# Configure PayPal
paypal_configure({
    "mode": os.environ.get('PAYPAL_MODE', 'sandbox'),
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET')
})

class PayPalPaymentService:
    @staticmethod
    async def create_payment(amount: float, return_url: str, cancel_url: str, description: str = "AfroMarket UK Purchase"):
        """Create a PayPal payment"""
        try:
            payment = PayPalPayment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "amount": {
                        "total": f"{amount:.2f}",
                        "currency": "GBP"
                    },
                    "description": description
                }]
            })
            
            if payment.create():
                # Get approval URL
                approval_url = None
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = link.href
                        break
                
                return {
                    "paymentId": payment.id,
                    "approvalUrl": approval_url,
                    "status": payment.state
                }
            else:
                raise HTTPException(status_code=400, detail=payment.error)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    async def execute_payment(payment_id: str, payer_id: str):
        """Execute/capture a PayPal payment"""
        try:
            payment = PayPalPayment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                return {
                    "paymentId": payment.id,
                    "status": payment.state,
                    "amount": float(payment.transactions[0].amount.total)
                }
            else:
                raise HTTPException(status_code=400, detail=payment.error)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    async def get_payment_details(payment_id: str):
        """Get payment details"""
        try:
            payment = PayPalPayment.find(payment_id)
            return {
                "paymentId": payment.id,
                "status": payment.state,
                "amount": float(payment.transactions[0].amount.total) if payment.transactions else 0
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))