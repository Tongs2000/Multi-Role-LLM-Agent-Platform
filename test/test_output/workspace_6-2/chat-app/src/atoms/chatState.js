import { atom } from 'jotai';

// Chat state
export const messagesAtom = atom([]);
export const onlineUsersAtom = atom([]);
export const connectionStatusAtom = atom('disconnected');

// Message actions
export const sendMessageAtom = atom(
  null,
  (get, set, { content, sender }) => {
    const newMessage = {
      id: Date.now(),
      content,
      sender,
      timestamp: new Date(),
    };
    set(messagesAtom, [...get(messagesAtom), newMessage]);
  }
);

// WebSocket actions
export const connectWebSocketAtom = atom(null, (get, set, url) => {
  const ws = new WebSocket(url);
  ws.onopen = () => set(connectionStatusAtom, 'connected');
  ws.onclose = () => set(connectionStatusAtom, 'disconnected');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'message') {
      set(messagesAtom, [...get(messagesAtom), data.payload]);
    } else if (data.type === 'presence') {
      set(onlineUsersAtom, data.payload);
    }
  };
  return () => ws.close();
});