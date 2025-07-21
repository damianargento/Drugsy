import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import { BACKEND_URL } from './config';
import './App.css';
import './Chat.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { PatientProvider, usePatient } from './contexts/PatientContext';
import { Patient } from './services/patientService';
import Sidebar from './components/sidebar/Sidebar';
import AuthButton from './components/auth/AuthButton';

// Message type definition
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function AppContent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { isLoggedIn, userInfo } = useAuth();
  const { selectedPatient } = usePatient();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message when component mounts
  useEffect(() => {
    setMessages([
      {
        role: 'assistant',
        content: "Hello! I'm Drugsy! I'm here to help doctors manage their patients' medications and provide information about drug interactions, side effects, and dietary recommendations. If you select a patient, I will provide personalized advice based on their medications and chronic conditions."
      }
    ]);
  }, []);


  // Handle sending a message
  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to the chat
    const userMessage: Message = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send message to the backend API using the config URL
      // Axios will automatically use the Authorization header set by our interceptors
      const response = await axios.post(`${BACKEND_URL}/chat`, {
        prompt: input,
        conversation_id: conversationId,
        patient_id: selectedPatient?.id
      });

      // Add assistant response to the chat
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
      };
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
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

  return (
    <>
      <header className="header">
        <img src="/images/logo.png" alt="Drugsy Logo" className="logo" />
        <AuthButton />
      </header>
      <main className="main">
      {isLoggedIn && <Sidebar /> }
      <div className="chat-container">
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
    </main>
    </>
  );
}

// Wrap the app with AuthProvider and PatientProvider
function App() {
  return (
    <AuthProvider>
      <PatientProvider>
        <AppContent />
      </PatientProvider>
    </AuthProvider>
  );
}

export default App;
