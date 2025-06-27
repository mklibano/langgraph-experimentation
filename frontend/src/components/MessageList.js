import React from 'react';
import './MessageList.css';

const MessageList = ({ messages, isLoading }) => {
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatContent = (content) => {
    // Simple formatting for better readability
    return content.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  return (
    <div className="message-list">
      {messages.length === 0 && !isLoading && (
        <div className="empty-state">
          <div className="empty-state-icon">💬</div>
          <h3>Start a conversation!</h3>
          <p>Ask me to count letters in any word. For example:</p>
          <ul>
            <li>"How many 'r's are in 'strawberry'?"</li>
            <li>"Count the letter 'e' in 'development'"</li>
            <li>"How many 'l's are in 'hello world'?"</li>
          </ul>
        </div>
      )}

      {messages.map((message, index) => (
        <div
          key={index}
          className={`message ${message.role === 'human' ? 'user-message' : 'agent-message'}`}
        >
          <div className="message-content">
            <div className="message-text">
              {formatContent(message.content)}
            </div>
            <div className="message-time">
              {formatTime(message.timestamp)}
            </div>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="message agent-message">
          <div className="message-content">
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageList; 