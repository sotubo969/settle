"""
AfroBot - AI Customer Service Chatbot for AfroMarket UK
Uses OpenAI GPT-4o directly with user's API key
"""
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import openai
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Try to use user's OpenAI key first, fallback to Emergent key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
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
   - Beauty & Household items (Black soap, Shea butter)

2. **Order Support**: Help with:
   - Tracking orders
   - Delivery information (UK-wide delivery)
   - Payment methods (Card, PayPal)
   - Returns and refunds

3. **Delivery Information**:
   - FREE delivery on orders over £100
   - Distance-based pricing for orders under £100
   - Same-day delivery available in London
   - UK-wide delivery within 2-5 days

4. **Cooking Tips**: Provide suggestions for:
   - Traditional African recipes (Jollof rice, Egusi soup, Fufu, etc.)
   - How to use specific ingredients
   - Food storage tips

5. **Business Hours & Contact**:
   - Operating hours: 24/7 online
   - Customer support email: sotubodammy@gmail.com
   - Website: afro-market.co.uk

Important guidelines:
- Always be respectful of all African cultures and cuisines
- If you don't know something, say so and offer to connect them with human support
- For specific order issues, always recommend contacting support at sotubodammy@gmail.com
- Promote the variety of authentic products from verified UK vendors
- Mention FREE delivery on orders over £100 when relevant
- Keep responses concise but helpful (max 3-4 sentences unless explaining recipes)
- Use emojis sparingly to add warmth to conversations

Remember: You represent AfroMarket UK, connecting African diaspora in the UK with authentic flavors from home! 🌍"""


# Store conversation history in memory (for simple session management)
_conversation_history: Dict[str, List[Dict[str, str]]] = {}


class AfroBotService:
    """AfroBot AI Chatbot Service using OpenAI"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY or EMERGENT_LLM_KEY
        self.model = "gpt-4o"
        
        if self.api_key:
            # Initialize OpenAI client
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            logger.info("AfroBot initialized with OpenAI")
        else:
            self.client = None
            logger.warning("No API key available for AfroBot")
    
    @staticmethod
    async def create_chat_session() -> str:
        """Create a new chat session ID"""
        session_id = str(uuid.uuid4())
        _conversation_history[session_id] = []
        return session_id
    
    async def get_chat_response(
        self,
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
        if not self.client:
            return "I'm sorry, but I'm having trouble connecting right now. Please try again later or contact support at sotubodammy@gmail.com"
        
        try:
            # Get or initialize conversation history for this session
            if session_id not in _conversation_history:
                _conversation_history[session_id] = []
            
            history = _conversation_history[session_id]
            
            # Build messages array
            messages = [
                {"role": "system", "content": AFROBOT_SYSTEM_PROMPT}
            ]
            
            # Add conversation history (last 10 messages to keep context manageable)
            for msg in history[-10:]:
                messages.append(msg)
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            
            assistant_message = response.choices[0].message.content
            
            # Store in history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": assistant_message})
            
            # Keep only last 20 messages
            if len(history) > 20:
                _conversation_history[session_id] = history[-20:]
            
            return assistant_message
            
        except openai.AuthenticationError:
            logger.error("OpenAI Authentication Error")
            return "I apologize, but I'm experiencing authentication issues. Please contact support at sotubodammy@gmail.com"
        except openai.RateLimitError:
            logger.error("OpenAI Rate Limit Error")
            return "I'm a bit busy right now! Please try again in a moment."
        except Exception as e:
            logger.error(f"AfroBot Error: {str(e)}")
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
• 🚚 Delivery info (FREE on orders over £100!)
• 🍳 Cooking tips and recipe ideas
• 💬 General inquiries

How can I assist you today?"""
    
    @staticmethod
    def clear_session(session_id: str) -> None:
        """Clear conversation history for a session"""
        if session_id in _conversation_history:
            del _conversation_history[session_id]


# Singleton instance
_afrobot_instance = None

def get_afrobot() -> AfroBotService:
    """Get AfroBot singleton instance"""
    global _afrobot_instance
    if _afrobot_instance is None:
        _afrobot_instance = AfroBotService()
    return _afrobot_instance
