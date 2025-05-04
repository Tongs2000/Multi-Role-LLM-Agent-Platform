import React from 'react';
import { Virtuoso } from 'react-virtuoso';
import { useAtomValue } from 'jotai';
import { messagesAtom } from '../atoms/chatState';

const VirtualizedMessageList = () => {
  const messages = useAtomValue(messagesAtom);

  const renderMessage = (index) => {
    const message = messages[index];
    return (
      <div key={message.id} className="message">
        <div className="message-sender">{message.sender}</div>
        <div className="message-content">{message.content}</div>
        <div className="message-timestamp">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    );
  };

  return (
    <Virtuoso
      totalCount={messages.length}
      itemContent={renderMessage}
      initialTopMostItemIndex={messages.length - 1}
      className="message-list"
    />
  );
};

export default VirtualizedMessageList;