# backend/simple_websocket_server.py
# Bloomberg APIなしで動作するテスト用サーバー

import asyncio
import json
import logging
import random
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockMarketDataService:
    """テスト用のモックデータサービス"""
    
    def __init__(self):
        self.connected_clients = set()
        self.securities = []
        self.base_prices = {
            'AAPL US Equity': 185.50,
            'MSFT US Equity': 425.30,
            'GOOGL US Equity': 140.20,
            'AMZN US Equity': 155.75,
            'TSLA US Equity': 240.80,
            '7203 JP Equity': 2850.00,
            '9984 JP Equity': 6200.00,
            'USDJPY Curncy': 150.25,
            'SPX Index': 4550.00,
            'NKY Index': 33500.00
        }
        self.prev_close_prices = {k: v * 0.99 for k, v in self.base_prices.items()}
        self.current_prices = self.base_prices.copy()
    
    async def broadcast_to_clients(self, data: dict):
        """全クライアントにデータを送信"""
        if self.connected_clients:
            message = json.dumps(data)
            disconnected = set()
            
            for client in self.connected_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            self.connected_clients -= disconnected
    
    async def generate_mock_data(self):
        """モックデータを生成して送信"""
        while True:
            await asyncio.sleep(1)  # 1秒ごとに更新
            
            for security in self.securities:
                if security in self.base_prices:
                    # ランダムな価格変動を生成
                    change = random.uniform(-0.5, 0.5)
                    self.current_prices[security] *= (1 + change / 100)
                    
                    # データを作成
                    last_price = self.current_prices[security]
                    prev_close = self.prev_close_prices[security]
                    change_pct = ((last_price - prev_close) / prev_close) * 100
                    
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "security": security,
                        "last_price": round(last_price, 2),
                        "prev_close": round(prev_close, 2),
                        "change_pct": round(change_pct, 4),
                        "bid": round(last_price * 0.999, 2),
                        "ask": round(last_price * 1.001, 2),
                        "volume": random.randint(1000000, 50000000)
                    }
                    
                    await self.broadcast_to_clients(data)

# サービスインスタンス
service = MockMarketDataService()

async def handle_websocket(websocket: WebSocketServerProtocol, path: str = None):
    """WebSocket接続を処理"""
    service.connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(service.connected_clients)}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if data.get("action") == "subscribe":
                    securities = data.get("securities", [])
                    if securities:
                        service.securities = securities
                        logger.info(f"Subscribed to: {securities}")
                        
                        # 確認メッセージを送信
                        await websocket.send(json.dumps({
                            "type": "subscription_confirmed",
                            "securities": securities
                        }))
                        
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {message}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        service.connected_clients.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(service.connected_clients)}")

async def main():
    """メイン実行関数"""
    # データ生成タスクを開始
    data_task = asyncio.create_task(service.generate_mock_data())
    
    # WebSocketサーバーを開始
    async with websockets.serve(handle_websocket, "localhost", 8765):
        logger.info("WebSocket server started on ws://localhost:8765")
        logger.info("This is a mock server for testing (no Bloomberg API required)")
        
        try:
            await asyncio.Future()  # 永続的に実行
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            data_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")