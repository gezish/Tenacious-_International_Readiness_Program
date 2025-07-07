import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
import json

# Load environment variables
load_dotenv()

# Debug: Print the OpenAI API key to verify it's loaded
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

class ShoppingAgent:
    def __init__(self):
        # Initialize OpenAI model
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",  # or "gpt-4", etc.
            temperature=0.7
        )
        
        # Initialize memory for conversation context
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # API base URLs
        self.product_api_url = os.getenv("PRODUCT_API_BASE_URL", "http://localhost:8001/api/products")
        self.user_api_url = os.getenv("USER_API_BASE_URL", "http://localhost:8001/api/users")
        self.checkout_api_url = os.getenv("CHECKOUT_API_BASE_URL", "http://localhost:8001/api/checkout")
        self.order_api_url = os.getenv("ORDER_API_BASE_URL", "http://localhost:8001/api/orders")
        
        # Current user context
        self.current_user_id = None
        self.user_preferences = {}
        
        # Create tools
        self.tools = [
            self.search_products_tool,
            self.get_product_details_tool,
            self.get_user_preferences_tool,
            self.update_user_preferences_tool,
            self.create_order_tool,
            self.get_order_status_tool,
            self.get_user_orders_tool
        ]
        
        # Create agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_agent(self):
        """Create the agent with shopping-specific prompt"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful and friendly shopping assistant for an e-commerce store. 
            Your goal is to help customers find and purchase products that match their needs and preferences.
            
            Key responsibilities:
            1. Greet customers warmly and ask about their shopping needs
            2. Gather customer preferences (budget, style, brand preferences, etc.)
            3. Search for products that match their criteria
            4. Present product recommendations with clear explanations
            5. Help customers compare products if needed
            6. Guide them through the purchase process
            7. Offer post-purchase support (tracking orders, returns, etc.)
            
            Always be:
            - Friendly and conversational
            - Helpful and informative
            - Patient with customer questions
            - Clear about product features and pricing
            - Proactive in offering relevant suggestions
            
            Use the available tools to search products, manage user preferences, and handle orders.
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        return create_openai_tools_agent(self.llm, self.tools, prompt)
    
    @tool
    def search_products_tool(self, query: str = "", category: str = "", min_price: Optional[float] = None, max_price: Optional[float] = None, brand: str = "") -> str:
        """Search for products based on criteria. Use this to find products that match customer needs."""
        try:
            params = {}
            if query:
                params["query"] = query
            if category:
                params["category"] = category
            if min_price is not None:
                params["min_price"] = min_price
            if max_price is not None:
                params["max_price"] = max_price
            if brand:
                params["brand"] = brand
            
            response = requests.get(f"{self.product_api_url}", params=params)
            response.raise_for_status()
            
            data = response.json()
            products = data.get("products", [])
            
            if not products:
                return "No products found matching your criteria. Would you like me to search with different parameters?"
            
            # Format product information
            result = f"Found {len(products)} products:\n\n"
            for i, product in enumerate(products[:5], 1):  # Show top 5
                result += f"{i}. **{product['name']}** - ${product['price']}\n"
                result += f"   Brand: {product['brand']} | Rating: {product['rating']}/5\n"
                result += f"   {product['description']}\n"
                result += f"   Features: {', '.join(product['features'])}\n\n"
            
            return result
            
        except requests.RequestException as e:
            return f"Sorry, I couldn't search for products right now. Error: {str(e)}"
    
    @tool
    def get_product_details_tool(self, product_id: str) -> str:
        """Get detailed information about a specific product by its ID."""
        try:
            response = requests.get(f"{self.product_api_url}/{product_id}")
            response.raise_for_status()
            
            product = response.json()
            
            result = f"**{product['name']}**\n\n"
            result += f"**Price:** ${product['price']}\n"
            result += f"**Brand:** {product['brand']}\n"
            result += f"**Rating:** {product['rating']}/5\n"
            result += f"**Category:** {product['category']}\n"
            result += f"**Description:** {product['description']}\n"
            result += f"**Features:** {', '.join(product['features'])}\n"
            result += f"**In Stock:** {'Yes' if product['in_stock'] else 'No'}\n"
            
            return result
            
        except requests.RequestException as e:
            return f"Sorry, I couldn't get product details. Error: {str(e)}"
    
    @tool
    def get_user_preferences_tool(self, user_id: str) -> str:
        """Get user preferences and purchase history to provide personalized recommendations."""
        try:
            response = requests.get(f"{self.user_api_url}/{user_id}")
            response.raise_for_status()
            
            user_data = response.json()
            preferences = user_data.get("preferences", {})
            purchase_history = user_data.get("purchase_history", [])
            
            result = f"**User Profile for {user_data['name']}**\n\n"
            
            if preferences:
                result += "**Preferences:**\n"
                if preferences.get("categories"):
                    result += f"- Preferred categories: {', '.join(preferences['categories'])}\n"
                if preferences.get("budget_range"):
                    budget = preferences["budget_range"]
                    result += f"- Budget range: ${budget.get('min', 0)} - ${budget.get('max', 1000)}\n"
                if preferences.get("brands"):
                    result += f"- Preferred brands: {', '.join(preferences['brands'])}\n"
            
            if purchase_history:
                result += f"\n**Recent Purchases:** {len(purchase_history)} items\n"
            
            return result
            
        except requests.RequestException as e:
            return f"Sorry, I couldn't get user preferences. Error: {str(e)}"
    
    @tool
    def update_user_preferences_tool(self, user_id: str, categories: str = "", budget_min: Optional[float] = None, budget_max: Optional[float] = None, brands: str = "") -> str:
        """Update user preferences based on their shopping behavior and feedback."""
        try:
            preferences = {}
            
            if categories:
                preferences["categories"] = [cat.strip() for cat in categories.split(",")]
            
            if budget_min is not None or budget_max is not None:
                preferences["budget_range"] = {}
                if budget_min is not None:
                    preferences["budget_range"]["min"] = budget_min
                if budget_max is not None:
                    preferences["budget_range"]["max"] = budget_max
            
            if brands:
                preferences["brands"] = [brand.strip() for brand in brands.split(",")]
            
            response = requests.put(
                f"{self.user_api_url}/{user_id}/preferences",
                json=preferences
            )
            response.raise_for_status()
            
            return "User preferences updated successfully! I'll use this information to provide better recommendations."
            
        except requests.RequestException as e:
            return f"Sorry, I couldn't update preferences. Error: {str(e)}"
    
    @tool
    def create_order_tool(self, user_id: str, product_id: str, quantity: int = 1) -> str:
        """Create a new order for the customer."""
        try:
            order_data = {
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity
            }
            
            response = requests.post(f"{self.checkout_api_url}", json=order_data)
            response.raise_for_status()
            
            order = response.json()
            
            result = f"🎉 **Order placed successfully!**\n\n"
            result += f"**Order ID:** {order['order_id']}\n"
            result += f"**Total Amount:** ${order['total_amount']}\n"
            result += f"**Status:** {order['status']}\n"
            result += f"**Order Date:** {order['created_at']}\n\n"
            result += "Your order has been confirmed and will be processed soon!"
            
            return result
            
        except requests.RequestException as e:
            return f"Sorry, I couldn't process your order. Error: {str(e)}"
    
    @tool
    def get_order_status_tool(self, order_id: str) -> str:
        """Check the status of a specific order."""
        try:
            response = requests.get(f"{self.order_api_url}/{order_id}")
            response.raise_for_status()
            
            order = response.json()
            
            result = f"**Order Status**\n\n"
            result += f"**Order ID:** {order['order_id']}\n"
            result += f"**Status:** {order['status']}\n"
            result += f"**Total Amount:** ${order['total_amount']}\n"
            result += f"**Order Date:** {order['created_at']}\n"
            
            return result
            
        except requests.RequestException as e:
            return f"Sorry, I couldn't check the order status. Error: {str(e)}"
    
    @tool
    def get_user_orders_tool(self, user_id: str) -> str:
        """Get all orders for a specific user."""
        try:
            response = requests.get(f"{self.order_api_url}/user/{user_id}")
            response.raise_for_status()
            
            data = response.json()
            orders = data.get("orders", [])
            
            if not orders:
                return "You don't have any orders yet."
            
            result = f"**Your Order History**\n\n"
            for i, order in enumerate(orders, 1):
                result += f"{i}. **Order ID:** {order['order_id']}\n"
                result += f"   **Status:** {order['status']}\n"
                result += f"   **Amount:** ${order['total_amount']}\n"
                result += f"   **Date:** {order['created_at']}\n\n"
            
            return result
            
        except requests.RequestException as e:
            return f"Sorry, I couldn't get your order history. Error: {str(e)}"
    
    def start_conversation(self, user_id: str = "user123"):
        """Start a conversation with the shopping assistant."""
        self.current_user_id = user_id
        
        # Get user preferences for context
        try:
            response = requests.get(f"{self.user_api_url}/{user_id}")
            if response.status_code == 200:
                user_data = response.json()
                self.user_preferences = user_data.get("preferences", {})
        except:
            pass
        
        welcome_message = f"""Hi! I'm your personal shopping assistant. I'm here to help you find the perfect products that match your style and budget.

I can help you with:
• Finding products based on your preferences
• Comparing different options
• Making purchases
• Tracking your orders
• And much more!

What are you looking for today?"""
        
        return welcome_message
    
    def chat(self, message: str) -> str:
        """Process a user message and return the agent's response."""
        try:
            response = self.agent_executor.invoke({"input": message})
            return response["output"]
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your request."

# Example usage
if __name__ == "__main__":
    # Initialize the shopping agent
    agent = ShoppingAgent()
    
    # Start conversation
    print(agent.start_conversation())
    
    # Interactive chat loop
    print("\n" + "="*50)
    print("Chat with your shopping assistant (type 'quit' to exit)")
    print("="*50)
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Shopping Assistant: Thanks for shopping with us! Have a great day!")
            break
        
        response = agent.chat(user_input)
        print(f"\nShopping Assistant: {response}") 