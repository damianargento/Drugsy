import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';
import './Chat.css';
import AuthButton from './components/auth/AuthButton';
import authService from './services/authService';

// Message type definition
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize authentication state from local storage
  useEffect(() => {
    authService.initAuthHeader();
    const token = authService.getToken();
    const storedUserInfo = authService.getUserInfo();
    
    if (token && storedUserInfo) {
      setIsLoggedIn(true);
      setUserInfo(storedUserInfo);
    }
  }, []);

  // Handle login
  const handleLogin = (token: string, userInfo: any) => {
    // Guardar el token y la información del usuario en localStorage
    authService.setToken(token);
    authService.setUserInfo(userInfo);
    
    // Actualizar el estado local
    setIsLoggedIn(true);
    setUserInfo(userInfo);
    
    console.log('Token guardado:', token);
  };

  // Handle logout
  const handleLogout = () => {
    authService.logout();
    setIsLoggedIn(false);
    setUserInfo(null);
  };

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to the chat
    const userMessage: Message = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Obtenemos el token
      const token = authService.getToken();
      console.log('Token enviado:', token);
      
      // Send message directly to the API
      const response = await axios.post('http://localhost:9000/chat', {
        prompt: input,
        conversation_id: conversationId,
      }, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        }
      });

      // Save the conversation ID for future messages
      if (!conversationId) {
        setConversationId(response.data.conversation_id);
      }

      // Add assistant response to the chat
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle pressing Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  // Get welcome message from backend when component mounts
  useEffect(() => {
    const getWelcomeMessage = async () => {
      try {
        const response = await axios.get('http://localhost:9000/welcome', {
          headers: {
            'Authorization': isLoggedIn ? `Bearer ${authService.getToken()}` : undefined,
          }
        });
        setMessages([
          {
            role: 'assistant',
            content: response.data.welcome_message,
          },
        ]);
      } catch (error) {
        console.error('Error fetching welcome message:', error);
        // Fallback welcome message if API call fails
        setMessages([
          {
            role: 'assistant',
            content: 'Hello! Welcome to Drugsy. How can I help you today?',
          },
        ]);
      }
    };
    
    getWelcomeMessage();
  }, []);

  return (
    <div className="chat-container">
      <header className="header">
        <img src="/images/logo.png" alt="Drugsy Logo" className="logo" />
        <AuthButton 
          isLoggedIn={isLoggedIn}
          userInfo={userInfo}
          onLogin={handleLogin}
          onLogout={handleLogout}
        />
      </header>
      <div className="messages-container">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.role === 'user' ? 'user-message' : 'bot-message'}`}
          >
            <div className="message-content">
              {message.role === 'assistant' ? (
                <ReactMarkdown>{message.content}</ReactMarkdown>
              ) : (
                message.content
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot-message">
            <div className="message-content loading">
              <div className="loading-spinner"></div>
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-container">
        <input
          type="text"
          placeholder="Ask about drug interactions with food..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          className="message-input"
        />
        <button 
          onClick={handleSendMessage}
          disabled={isLoading}
          className="send-button"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default App;
