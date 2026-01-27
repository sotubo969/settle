import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Send, ArrowLeft, Loader2, User, Clock, CheckCheck } from 'lucide-react';
import axios from 'axios';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import { ScrollArea } from '../components/ui/scroll-area';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Messages = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchConversations();
  }, [isAuthenticated]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const token = localStorage.getItem('afroToken');
      const response = await axios.get(`${API}/messages`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversations(response.data.conversations);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      const token = localStorage.getItem('afroToken');
      const response = await axios.get(`${API}/messages/${conversationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data.messages);
    } catch (error) {
      toast.error('Failed to load messages');
    }
  };

  const selectConversation = (conv) => {
    setSelectedConversation(conv);
    fetchMessages(conv.conversation_id);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConversation) return;

    setSendingMessage(true);
    try {
      const token = localStorage.getItem('afroToken');
      await axios.post(`${API}/messages`, {
        receiver_id: selectedConversation.other_user.id,
        message: newMessage,
        order_id: selectedConversation.order_id
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNewMessage('');
      fetchMessages(selectedConversation.conversation_id);
    } catch (error) {
      toast.error('Failed to send message');
    } finally {
      setSendingMessage(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-3" data-testid="messages-title">
          <MessageSquare className="w-8 h-8 text-emerald-600" />
          Messages
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[600px]">
          {/* Conversations List */}
          <Card className="md:col-span-1 overflow-hidden">
            <CardHeader className="border-b">
              <CardTitle className="text-lg">Conversations</CardTitle>
            </CardHeader>
            <ScrollArea className="h-[500px]">
              {conversations.length === 0 ? (
                <div className="p-6 text-center">
                  <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No conversations yet</p>
                </div>
              ) : (
                <div className="divide-y">
                  {conversations.map((conv) => (
                    <button
                      key={conv.conversation_id}
                      onClick={() => selectConversation(conv)}
                      className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                        selectedConversation?.conversation_id === conv.conversation_id 
                          ? 'bg-emerald-50 border-l-4 border-emerald-500' 
                          : ''
                      }`}
                      data-testid={`conversation-${conv.conversation_id}`}
                    >
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarImage src={conv.other_user.avatar} />
                          <AvatarFallback>
                            {conv.other_user.name?.charAt(0) || 'U'}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-center">
                            <p className="font-medium text-gray-900 truncate">
                              {conv.other_user.name}
                            </p>
                            {conv.unread_count > 0 && (
                              <Badge className="bg-emerald-500 text-white text-xs">
                                {conv.unread_count}
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-500 truncate">
                            {conv.last_message}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {new Date(conv.last_message_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </ScrollArea>
          </Card>

          {/* Messages Area */}
          <Card className="md:col-span-2 flex flex-col overflow-hidden">
            {selectedConversation ? (
              <>
                {/* Chat Header */}
                <CardHeader className="border-b flex-shrink-0">
                  <div className="flex items-center gap-3">
                    <button 
                      className="md:hidden"
                      onClick={() => setSelectedConversation(null)}
                    >
                      <ArrowLeft className="w-5 h-5" />
                    </button>
                    <Avatar>
                      <AvatarImage src={selectedConversation.other_user.avatar} />
                      <AvatarFallback>
                        {selectedConversation.other_user.name?.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-semibold">{selectedConversation.other_user.name}</p>
                      {selectedConversation.order_id && (
                        <p className="text-xs text-gray-500">
                          Order #{selectedConversation.order_id}
                        </p>
                      )}
                    </div>
                  </div>
                </CardHeader>

                {/* Messages */}
                <ScrollArea className="flex-1 p-4">
                  <div className="space-y-4">
                    {messages.map((msg) => (
                      <div 
                        key={msg.id}
                        className={`flex ${msg.is_mine ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-[70%] ${
                          msg.is_mine 
                            ? 'bg-emerald-500 text-white rounded-l-lg rounded-tr-lg' 
                            : 'bg-gray-100 text-gray-900 rounded-r-lg rounded-tl-lg'
                        } p-3`}>
                          <p className="text-sm">{msg.message}</p>
                          <div className={`flex items-center gap-1 mt-1 text-xs ${
                            msg.is_mine ? 'text-emerald-100' : 'text-gray-400'
                          }`}>
                            <Clock className="w-3 h-3" />
                            {new Date(msg.created_at).toLocaleTimeString('en-GB', {
                              hour: '2-digit', minute: '2-digit'
                            })}
                            {msg.is_mine && msg.read && (
                              <CheckCheck className="w-3 h-3 ml-1" />
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                </ScrollArea>

                {/* Message Input */}
                <form onSubmit={sendMessage} className="p-4 border-t flex gap-2">
                  <Input 
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type a message..."
                    className="flex-1"
                    data-testid="message-input"
                  />
                  <Button 
                    type="submit" 
                    disabled={sendingMessage || !newMessage.trim()}
                    className="bg-emerald-600 hover:bg-emerald-700"
                    data-testid="send-message-btn"
                  >
                    {sendingMessage ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </form>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Select a conversation to start messaging</p>
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Messages;
