import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage = {
      role: 'human',
      content: messageText,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await axios.post('/api/chat', {
        message: messageText,
        thread_id: threadId
      });

      // Update thread ID if it's new
      if (!threadId && response.data.thread_id) {
        setThreadId(response.data.thread_id);
      }

      // Add agent response
      const agentMessage = {
        role: 'ai',
        content: response.data.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, agentMessage]);

    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Remove the user message if sending failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = async () => {
    if (threadId) {
      try {
        await axios.delete(`/api/conversations/${threadId}`);
      } catch (err) {
        console.error('Error clearing conversation:', err);
      }
    }
    setMessages([]);
    setThreadId(null);
    setError(null);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="chat-status">
          {messages.length === 0 && (
            <span className="welcome-message">
              Try asking: "How many 'r's are in 'strawberry'?"
            </span>
          )}
          {messages.length > 0 && (
            <button 
              onClick={clearConversation}
              className="clear-button"
              disabled={isLoading}
            >
              Clear Chat
            </button>
          )}
        </div>
      </div>

      <div className="messages-container">
        <MessageList 
          messages={messages} 
          isLoading={isLoading}
        />
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)} className="error-close">×</button>
        </div>
      )}

      <MessageInput 
        onSendMessage={sendMessage}
        disabled={isLoading}
        placeholder={isLoading ? "Thinking..." : "Ask me to count letters in a word..."}
      />
    </div>
  );
};

export default ChatInterface; 