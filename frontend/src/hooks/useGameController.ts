import { useState, useEffect, useRef, useCallback } from 'react';
import { Telemetry } from '../types/game';

export interface Message {
  id: string;
  sender: 'Mission Control' | 'Jack' | 'System';
  text: string;
}

const DEFAULT_TELEMETRY: Telemetry = {
    co2: 0.04,
    temp: 20.0,
    heart_rate: 70,
    pressure: 101.3,
    o2: 21.0,
    battery: 100.0,
    power_draw: 0.0,
    stress: 0.0,
    inventory: []
};

export const useGameController = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [telemetry, setTelemetry] = useState<Telemetry>(DEFAULT_TELEMETRY);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket Server
    // Use relative protocol (ws:// or wss://) based on current page
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
    const wsUrl = `${protocol}//${host}/ws`;
    
    const socket = new WebSocket(wsUrl);
    ws.current = socket;

    socket.onopen = () => {
        console.log('[CLIENT] Connected to Game Engine');
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('[CLIENT] Received:', data);

        // Update Telemetry if present
        if (data.telemetry) {
            setTelemetry(data.telemetry);
        }

        // Handle Message Types
        if (data.type === 'INIT') {
             setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'System', text: data.message }]);
        } else if (data.type === 'TICK') {
            // Telemetry update handled above
            if (data.sensory) {
                 // Optional: Log sensory data to console or a debug panel
                 console.log('[SENSORY]', data.sensory);
            }
        } else if (data.type === 'RESPONSE' || data.type === 'UPDATE' || data.type === 'WIN' || data.type === 'GAME_OVER' || data.type === 'INTERCEPT') {
            setIsTyping(false);
            if (data.jack_response) {
                setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'Jack', text: data.jack_response }]);
            }
            if (data.message) { // System message (e.g. Game Over)
                setMessages(prev => [...prev, { id: (Date.now()+1).toString(), sender: 'System', text: data.message }]);
            }
        }
    };

    socket.onclose = () => {
        console.log('[CLIENT] Disconnected');
        setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'System', text: 'CONNECTION LOST. RECONNECTING...' }]);
    };

    return () => {
        socket.close();
    };
  }, []);

  const sendMessage = useCallback((text: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        // Add user message to UI immediately
        const userMsg: Message = { id: Date.now().toString(), sender: 'Mission Control', text };
        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        // Send to Backend
        ws.current.send(JSON.stringify({ text }));
    } else {
        console.error("WebSocket not connected");
    }
  }, []);

  return {
    messages,
    sendMessage,
    isTyping,
    telemetry
  };
};
