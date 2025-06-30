import { useState, useRef, useEffect } from 'react';
import './App.css';
import Chatbot from './components/Chatbot';
import ChatIcon from './assets/WatsonAssistant.svg';

function App() {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const chatbotRef = useRef(null);

  const toggleChatbot = () => {
    setIsChatbotOpen((prev) => !prev);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (chatbotRef.current && !chatbotRef.current.contains(event.target)) {
        setIsChatbotOpen(false);
      }
    };

    if (isChatbotOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isChatbotOpen]);

  return (
    <div className="App">
      <button className="chat-toggle-button" onClick={toggleChatbot}>
        <img src={ChatIcon} alt="Chat Icon" width="24" height="24" />
      </button>

      {isChatbotOpen && (
        <div ref={chatbotRef}>
          <Chatbot onClose={() => setIsChatbotOpen(false)} />
        </div>
      )}
    </div>
  );
}

export default App
