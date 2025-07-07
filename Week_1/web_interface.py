from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
from shopping_agent import ShoppingAgent

app = FastAPI(title="Shopping Assistant API", version="1.0.0")

# Initialize shopping agent
shopping_agent = ShoppingAgent()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# Pydantic models
class ChatMessage(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    user_id: str

# HTML template for the chat interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Shopping Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
        }
        .message.user {
            justify-content: flex-end;
        }
        .message.assistant {
            justify-content: flex-start;
        }
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.user .message-content {
            background: #667eea;
            color: white;
        }
        .message.assistant .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        .chat-input {
            padding: 20px;
            border-top: 1px solid #e0e0e0;
            background: white;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        #messageInput {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        #sendButton {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
        }
        #sendButton:hover {
            background: #5a6fd8;
        }
        .typing-indicator {
            display: none;
            color: #666;
            font-style: italic;
            margin-bottom: 10px;
        }
        .product-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .product-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .product-price {
            color: #667eea;
            font-weight: bold;
        }
        .product-description {
            color: #666;
            font-size: 14px;
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🛍️ Shopping Assistant</h1>
            <p>Your personal AI shopping companion</p>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message assistant">
                <div class="message-content">
                    Hi! I'm your personal shopping assistant. I'm here to help you find the perfect products that match your style and budget. What are you looking for today?
                </div>
            </div>
        </div>
        <div class="typing-indicator" id="typingIndicator">
            Shopping Assistant is typing...
        </div>
        <div class="chat-input">
            <div class="input-group">
                <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                <button id="sendButton" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        let ws = new WebSocket("ws://localhost:8000/ws");
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            addMessage(data.response, 'assistant');
            document.getElementById('typingIndicator').style.display = 'none';
        };
        
        ws.onopen = function(event) {
            console.log("Connected to shopping assistant");
        };
        
        ws.onclose = function(event) {
            console.log("Disconnected from shopping assistant");
        };
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message) {
                addMessage(message, 'user');
                input.value = '';
                
                // Show typing indicator
                document.getElementById('typingIndicator').style.display = 'block';
                
                // Send message to server
                ws.send(JSON.stringify({
                    user_id: "user123",
                    message: message
                }));
            }
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function addMessage(message, sender) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // Check if message contains product information (simple heuristic)
            if (message.includes('**') && message.includes('$')) {
                // Format as product cards
                const lines = message.split('\\n');
                let formattedMessage = '';
                
                for (let line of lines) {
                    if (line.includes('**') && line.includes('$')) {
                        // This looks like a product line
                        const productMatch = line.match(/\\*\\*(.*?)\\*\\* - \\$(\\d+\\.\\d+)/);
                        if (productMatch) {
                            formattedMessage += `<div class="product-card">
                                <div class="product-name">${productMatch[1]}</div>
                                <div class="product-price">$${productMatch[2]}</div>
                            </div>`;
                        } else {
                            formattedMessage += line + '<br>';
                        }
                    } else {
                        formattedMessage += line + '<br>';
                    }
                }
                contentDiv.innerHTML = formattedMessage;
            } else {
                contentDiv.textContent = message;
            }
            
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    </script>
</body>
</html>
"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the chat interface"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message with shopping agent
            response = shopping_agent.chat(message_data["message"])
            
            # Send response back
            await manager.send_personal_message(
                json.dumps({"response": response, "user_id": message_data["user_id"]}),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """REST API endpoint for chat"""
    try:
        response = shopping_agent.chat(chat_message.message)
        return ChatResponse(response=response, user_id=chat_message.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start-conversation")
async def start_conversation(user_id: str = "user123"):
    """Start a new conversation with the shopping assistant"""
    try:
        welcome_message = shopping_agent.start_conversation(user_id)
        return {"message": welcome_message, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "shopping-assistant"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8016) 