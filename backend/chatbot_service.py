"""
AfroBot - AI Customer Service Chatbot for AfroMarket UK
Uses Emergent LLM Integration with GPT-4o
"""
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")

# AfroBot System Prompt - Customer Service for African Grocery E-commerce
AFROBOT_SYSTEM_PROMPT = """You are AfroBot, a friendly and knowledgeable AI customer service assistant for AfroMarket UK - the premier online marketplace for authentic African groceries in the United Kingdom.

Your personality:
- Warm, friendly, and culturally aware
- Knowledgeable about African food products, cuisines, and cooking traditions
- Professional but with a personal touch
- Patient and helpful with all customer inquiries

Your capabilities:
1. **Product Information**: Help customers find African food products like:
   - Grains & Flours (Garri, Fufu, Semolina, Pounded Yam flour)
   - Fresh Produce (Plantains, Yams, Cassava, Scotch Bonnets)
   - Condiments & Seasonings (Palm oil, Maggi, Crayfish, Locust beans)
   - Frozen Foods & Meats
   - Snacks & Confectionery
   - Drinks & Beverages

2. **Order Support**: Help with:
   - Tracking orders
   - Delivery information (UK-wide delivery)
   - Payment methods (Card, PayPal, Apple Pay)
   - Returns and refunds

3. **Cooking Tips**: Provide suggestions for:
   - Traditional African recipes
   - How to use specific ingredients
   - Food storage tips

4. **Business Hours & Contact**:
   - Operating hours: 24/7 online
   - Customer support email: sotubodammy@gmail.com
   - Delivery: Same-day available in select areas

Important guidelines:
- Always be respectful of all African cultures and cuisines
- If you don't know something, say so and offer to connect them with human support
- For specific order issues, always recommend contacting support at sotubodammy@gmail.com
- Promote the variety of authentic products from verified UK vendors
- Mention free delivery on orders over £70 when relevant
- Keep responses concise but helpful (max 3-4 sentences unless explaining recipes)

Remember: You represent AfroMarket UK, connecting African diaspora in the UK with authentic flavors from home! 🌍"""


class AfroBotService:
    """AfroBot AI Chatbot Service"""
    
    @staticmethod
    async def create_chat_session() -> str:
        """Create a new chat session ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    async def get_chat_response(
        message: str, 
        session_id: str,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Get AI response from AfroBot
        
        Args:
            message: User's message
            session_id: Unique session identifier
            chat_history: Previous messages in the conversation
            
        Returns:
            AI response string
        """
        if not EMERGENT_LLM_KEY:
            return "I'm sorry, but I'm having trouble connecting right now. Please try again later or contact support at sotubodammy@gmail.com"
        
        try:
            # Initialize the chat with system message
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=session_id,
                system_message=AFROBOT_SYSTEM_PROMPT
            )
            
            # Use GPT-4o model
            chat.with_model("openai", "gpt-4o")
            
            # Create user message
            user_message = UserMessage(text=message)
            
            # Get response
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            print(f"AfroBot Error: {str(e)}")
            return "I apologize, but I'm experiencing some technical difficulties. Please try again in a moment, or contact our support team at sotubodammy@gmail.com for immediate assistance."
    
    @staticmethod
    def get_quick_replies() -> List[Dict[str, str]]:
        """Get suggested quick reply options"""
        return [
            {"id": "products", "text": "🛒 Browse Products"},
            {"id": "tracking", "text": "📦 Track My Order"},
            {"id": "delivery", "text": "🚚 Delivery Info"},
            {"id": "recipes", "text": "🍳 Recipe Ideas"},
            {"id": "support", "text": "💬 Contact Support"}
        ]
    
    @staticmethod
    def get_welcome_message() -> str:
        """Get the welcome message for new chat sessions"""
        return """Hello! 👋 I'm **AfroBot**, your friendly assistant at AfroMarket UK!

I'm here to help you with:
• 🛒 Finding authentic African products
• 📦 Order tracking and delivery questions
• 🍳 Cooking tips and recipe ideas
• 💬 General inquiries

How can I assist you today?"""
