import { useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import './Chatbot.css';
import Message from './Message';
import InputBox from './InputBox';
import MinimiseIcon from '../assets/Minimise.svg'
import MaximiseIcon from '../assets/Maximise.svg'
import CloseIcon from '../assets/Close.svg'
import DownloadIcon from '../assets/downloadIcon.svg'

const Chatbot= ({ onClose }) => {
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    { text: "Hi! I'm your chatbot. How can I help you?", sender: 'bot' }
  ]);
  const apiProtocol = import.meta.env.VITE_CHATBOT_API_PROTOCOL;
  const apiHost= import.meta.env.VITE_CHATBOT_API_HOST;
  const apiPort = import.meta.env.VITE_CHATBOT_API_PORT;
  const apiUrl = `${apiProtocol}://${apiHost}:${apiPort}`;

  const handleSendMessage = async (query) => {
    try {
      const response = await axios.get(`${apiUrl}/data`, { params: { query } });

      const data = response.data.sections;

      const textResponse = data.find((section) => section.type === 'text')?.data || '';
      const tableResponse = data.find((section) => section.type === 'table')?.data || [];

      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: textResponse },
        { sender: 'bot', type: 'table', data: tableResponse },
      ]);
    } catch (error) {
      console.error('We are unable to fetch query : ', error);
      setMessages((prev) => [
        ...prev,
        { sender: 'Bot', message: 'Something went wrong. Please try again later.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleUserMessage = (text) => {
    if (!text.trim()) return;
    const userMessage = { text, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setLoading(true);
  
    // Add bot response with a delay to avoid duplication
    setTimeout(() => {
      const botReply = generateBotResponse(text);
      console.info('MBM getting botReply: ', botReply);
      botReply && setMessages((prevMessages) => [...prevMessages, botReply]);
      setLoading(false);
    }, 500); // Delay in ms for a more natural response
  };
  

  const generateBotResponse = (userInput) => {
    let botResponseText = 'Sorry, I am just a basic bot.';
    if (userInput.toLowerCase().includes('hello')) {
      botResponseText = 'Hello there! How can I assist you today?';
      return { text: botResponseText, sender: 'bot' };
    } else if (userInput.toLowerCase().includes('bye')) {
      botResponseText = 'Goodbye! Have a great day!';
      return { text: botResponseText, sender: 'bot' };
    }
    else {
      handleSendMessage(userInput);
    }
  };

  // Toggle minimize state
  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  // Toggle maximize state
  const toggleMaximize = () => {
    setIsMaximized(!isMaximized);
    setIsMinimized(false); // Ensure it's not minimized when maximized
  };

  const downloadChat = () => {
    console.info('MBM  clicked download');
    const chatHistory = messages
  .map(message => {
    const content = message.type !== 'table' ? message.text : message.data;
    return `${message?.sender}: ${JSON.stringify(content)}`;
  })
  .join('\n');
    const blob = new Blob([chatHistory], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'chat_history.txt';
    document.body.appendChild(a);
    a.click();

    // Clean up the object URL after download
    URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  return (
    <div
      className={`chatbot ${isMinimized ? 'minimized' : ''} ${isMaximized ? 'maximized' : ''}`}
    >
      {/* Header with controls */}
      <div className="chatbot-header">
        <span className="chatbot-title">Chatbot</span>
        <div className="chatbot-controls">
          <button onClick={downloadChat}>
            <img src={DownloadIcon} alt='Download Icon' width="15" height="15"/>
          </button>
          <button onClick={toggleMinimize}>
            <img src={MinimiseIcon} alt='Minimize Icon' width="15" height="15"/>
          </button>
          <button onClick={toggleMaximize}>
          <img src={MaximiseIcon} alt='Maximize Icon' width="15" height="15"/>
          </button>
          <button onClick={onClose}>
          <img src={CloseIcon} alt='Close Icon' width="15" height="15"/>
          </button>
        </div>
      </div>

      {/* Chat history and input box, hidden when minimized */}
      {!isMinimized && (
        <div className="chatbot-content">
          <div className="chat-history">
            {messages.map((chat, index) => (
              <div key={index} className={`chat-message-${chat?.sender?.toLowerCase()}`}>
                <Message key={index} text={chat?.text} sender={chat?.sender} type={chat?.type} data={chat?.data} />
              </div>
            ))}
            {loading && <p className="loading">Loading...</p>}
          </div>
          <div>
            <InputBox onSendMessage={handleUserMessage} />
          </div>
        </div>
      )}
    </div>
  );
};

Chatbot.propTypes = {
  onClose: PropTypes.func.isRequired, // Add validation for the onClose prop
};

export default Chatbot;
