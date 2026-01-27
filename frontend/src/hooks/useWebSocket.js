import { useState, useEffect, useCallback, useRef } from 'react';

const WS_URL = process.env.REACT_APP_BACKEND_URL?.replace('https://', 'wss://').replace('http://', 'ws://');

export function useWebSocket(vendorId, onNotification) {
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const pingIntervalRef = useRef(null);

  const connect = useCallback(() => {
    if (!vendorId || !WS_URL) {
      console.log('WebSocket: Missing vendor ID or URL');
      return;
    }

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `${WS_URL}/ws/vendor/${vendorId}`;
    console.log('WebSocket: Connecting to', wsUrl);

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket: Connected');
        setIsConnected(true);
        setReconnectAttempt(0);

        // Start ping interval to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket: Message received', data.type);

          if (data.type === 'notification' && onNotification) {
            onNotification(data.notification);
          } else if (data.type === 'pong') {
            // Heartbeat response
          }
        } catch (err) {
          console.error('WebSocket: Message parse error', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket: Error', error);
      };

      ws.onclose = (event) => {
        console.log('WebSocket: Disconnected', event.code, event.reason);
        setIsConnected(false);

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }

        // Reconnect with exponential backoff
        if (event.code !== 1000) { // Not a clean close
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempt), 30000);
          console.log(`WebSocket: Reconnecting in ${delay}ms`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempt(prev => prev + 1);
            connect();
          }, delay);
        }
      };
    } catch (err) {
      console.error('WebSocket: Connection error', err);
    }
  }, [vendorId, onNotification, reconnectAttempt]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnect');
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    if (vendorId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [vendorId]); // Only reconnect when vendorId changes

  return {
    isConnected,
    reconnectAttempt,
    connect,
    disconnect
  };
}

export default useWebSocket;
