// frontend/app/hooks/useWebSocket.ts

import { useState, useEffect, useRef } from 'react';
import { MarketData } from '../types/market';

export const useWebSocket = (url: string) => {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      const newData = JSON.parse(event.data) as MarketData;
      setMarketData((prevData) => [...prevData, newData]);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    // クリーンアップ
    return () => {
      ws.current?.close();
    };
  }, [url]);

  return { marketData, isConnected };
};