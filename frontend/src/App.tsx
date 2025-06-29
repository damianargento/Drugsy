import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { BACKEND_URL } from './config';
import './App.css';
import './Chat.css';
import AuthButton from './components/auth/AuthButton';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import PatientManagement from './components/patients/PatientManagement';
import { Patient } from './services/patientService';

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
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const { isLoggedIn, userInfo } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  // Handle sending a message
  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to the chat
    const userMessage: Message = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Get token from localStorage
      const token = localStorage.getItem('token');
      
      // Send message to the backend API using the config URL
      const response = await axios.post(`${BACKEND_URL}/chat`, {
        prompt: input,
        conversation_id: conversationId,
        patient_id: selectedPatient?.id || null,
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
        const response = await axios.get(`${BACKEND_URL}/welcome`, {
          headers: {
            'Authorization': isLoggedIn ? `Bearer ${localStorage.getItem('token')}` : undefined,
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

  const handlePatientSelect = (patient: Patient | null) => {
    setSelectedPatient(patient);
    // You could add additional logic here, such as loading patient-specific chat history
  };

  return (
    <div className="chat-container">
      <header className="header">
        <img src="/images/logo.png" alt="Drugsy Logo" className="logo" />
        <AuthButton />
      </header>
      
      {isLoggedIn && (
        <div className="patient-section">
          <PatientManagement 
            onPatientSelect={handlePatientSelect}
            selectedPatientId={selectedPatient?.id}
          />
        </div>
      )}
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

// Wrap the app with AuthProvider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
