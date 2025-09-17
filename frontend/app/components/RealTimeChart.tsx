// frontend/app/components/RealTimeChart.tsx

'use client';

import React from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import PriceCard from './PriceCard'; // SecuritySelector.tsx の実体
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { ja } from 'date-fns/locale';

// Chart.js の設定
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const RealTimeChart: React.FC = () => {
  const { marketData, isConnected } = useWebSocket('ws://localhost:8765');
  const security = '7203 JT Equity';

  // チャート用のデータ
  const chartData = {
    labels: marketData.map((data) => new Date(data.timestamp)),
    datasets: [
      {
        label: `${security} Price`,
        data: marketData.map((data) => data.last_price),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.1,
      },
    ],
  };

  // チャートのオプション
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'リアルタイム価格チャート',
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'minute' as const,
          tooltipFormat: 'PPpp',
        },
        adapters: {
          date: {
            locale: ja,
          },
        },
        title: {
          display: true,
          text: '時刻',
        },
      },
      y: {
        title: {
          display: true,
          text: '価格',
        },
      },
    },
  };

  const latestData = marketData.length > 0 ? marketData[marketData.length - 1] : null;

  return (
    <div className="container mx-auto p-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Bloomberg Real-Time Market Data</h1>
        <p className="text-md text-gray-600">
          接続ステータス: 
          <span className={`ml-2 font-semibold ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
            {isConnected ? '接続中' : '切断'}
          </span>
        </p>
      </header>

      {latestData && (
        <div className="mb-8">
          <PriceCard security={security} data={latestData} />
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-4">
        <Line options={options} data={chartData} />
      </div>
    </div>
  );
};

export default RealTimeChart;