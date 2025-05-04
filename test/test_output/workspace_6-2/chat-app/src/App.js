import React from 'react';
import { useChatStore } from './context/useChatStore';
import MessageList from './components/MessageList';
import ChatInput from './components/ChatInput';
import './styles/global.css';

export default function App() {
  const { messages, sendMessage } = useChatStore();

  return (
    <div className="app">
      <h1>Chat Application</h1>
      <MessageList messages={messages} />
      <ChatInput onSendMessage={sendMessage} />
    </div>
  );
}