import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Bot, User, Loader2, ChevronDown, Sparkles } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

const AfroBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [quickReplies, setQuickReplies] = useState([]);
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Load welcome message when chat opens
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      loadWelcomeMessage();
    }
  }, [isOpen]);

  const loadWelcomeMessage = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/chatbot/welcome`);
      const data = await response.json();
      
      if (data.success) {
        setSessionId(data.session_id);
        setMessages([{
          role: 'assistant',
          content: data.welcome_message || data.message || "Hello! 👋 I'm AfroBot. How can I help you today?",
          timestamp: new Date().toISOString()
        }]);
        setQuickReplies(data.quick_replies || []);
      } else {
        throw new Error('Failed to load welcome');
      }
    } catch (error) {
      console.error('Error loading welcome message:', error);
      setMessages([{
        role: 'assistant',
        content: "Hello! 👋 I'm AfroBot, your friendly assistant at AfroMarket UK! How can I help you today?",
        timestamp: new Date().toISOString()
      }]);
      setQuickReplies([
        { id: 'products', text: '🛒 Browse Products' },
        { id: 'delivery', text: '🚚 Delivery Info' },
        { id: 'support', text: '💬 Contact Support' }
      ]);
    }
  };

  const sendMessage = async (messageText) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: messageText.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setShowQuickReplies(false);

    try {
      const response = await fetch(`${BACKEND_URL}/api/chatbot/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText.trim(),
          session_id: sessionId
        })
      });

      const data = await response.json();

      if (data.success) {
        setSessionId(data.session_id);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp
        }]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I apologize, but I'm having trouble connecting right now. Please try again or contact support at sotubodammy@gmail.com",
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const handleQuickReply = (reply) => {
    const quickMessages = {
      products: "What products do you have available?",
      tracking: "How can I track my order?",
      delivery: "Tell me about your delivery options",
      recipes: "Can you suggest some African recipes?",
      support: "I need to speak with customer support"
    };
    
    sendMessage(quickMessages[reply.id] || reply.text);
  };

  // Format message with markdown-like styling
  const formatMessage = (content) => {
    // Handle bold text with **
    let formatted = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Handle bullet points
    formatted = formatted.replace(/^• /gm, '<span class="text-green-600 mr-1">•</span>');
    formatted = formatted.replace(/^- /gm, '<span class="text-green-600 mr-1">•</span>');
    // Handle line breaks
    formatted = formatted.split('\n').map((line, i) => (
      <span key={i} dangerouslySetInnerHTML={{ __html: line }} className="block" />
    ));
    return formatted;
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        data-testid="chatbot-toggle-button"
        className={`fixed bottom-6 right-6 z-50 p-4 rounded-full shadow-lg transition-all duration-300 transform hover:scale-110 ${
          isOpen 
            ? 'bg-red-500 hover:bg-red-600 rotate-0' 
            : 'bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600'
        }`}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <div className="relative">
            <MessageCircle className="w-6 h-6 text-white" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-orange-500 rounded-full animate-pulse" />
          </div>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div 
          data-testid="chatbot-window"
          className="fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-200 animate-slideUp"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-green-600 to-green-500 p-4 text-white">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                  <Bot className="w-7 h-7" />
                </div>
                <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-300 rounded-full border-2 border-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg flex items-center gap-2">
                  AfroBot
                  <Sparkles className="w-4 h-4 text-yellow-300" />
                </h3>
                <p className="text-green-100 text-sm">Your African Grocery Assistant</p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-white/20 rounded-full transition-colors"
              >
                <ChevronDown className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="h-80 overflow-y-auto p-4 bg-gray-50 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-2 ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-orange-100 text-orange-600'
                }`}>
                  {message.role === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
                <div className={`max-w-[75%] px-4 py-3 rounded-2xl ${
                  message.role === 'user'
                    ? 'bg-green-600 text-white rounded-tr-md'
                    : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-tl-md'
                }`}>
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.role === 'assistant' 
                      ? formatMessage(message.content)
                      : message.content
                    }
                  </div>
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex gap-2">
                <div className="w-8 h-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-md shadow-sm border border-gray-100">
                  <div className="flex items-center gap-2 text-gray-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Replies */}
          {showQuickReplies && quickReplies.length > 0 && (
            <div className="px-4 py-2 bg-white border-t border-gray-100">
              <div className="flex flex-wrap gap-2">
                {quickReplies.map((reply) => (
                  <button
                    key={reply.id}
                    onClick={() => handleQuickReply(reply)}
                    className="text-xs px-3 py-1.5 bg-green-50 text-green-700 rounded-full border border-green-200 hover:bg-green-100 transition-colors"
                  >
                    {reply.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-100">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                data-testid="chatbot-input"
                className="flex-1 px-4 py-2 bg-gray-100 rounded-full border-0 focus:ring-2 focus:ring-green-500 focus:outline-none text-sm"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                data-testid="chatbot-send-button"
                className="p-2 bg-green-600 text-white rounded-full hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-gray-400 text-center mt-2">
              Powered by AfroMarket UK AI
            </p>
          </form>
        </div>
      )}

      {/* Animation styles */}
      <style jsx>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideUp {
          animation: slideUp 0.3s ease-out;
        }
      `}</style>
    </>
  );
};

export default AfroBot;
