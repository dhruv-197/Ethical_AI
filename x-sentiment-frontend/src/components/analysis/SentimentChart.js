import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const SentimentChart = ({ analysisResults }) => {
  if (!analysisResults) return null;

  const data = {
    labels: ['Radical', 'Non-Radical', 'Political', 'Crime'],
    datasets: [
      {
        data: [
          analysisResults.radical_score,
          100 - analysisResults.radical_score,
          analysisResults.political_score,
          analysisResults.crime_score,
        ],
        backgroundColor: [
          '#ef4444', // red for radical
          '#22c55e', // green for non-radical
          '#3b82f6', // blue for political
          '#f59e0b', // amber for crime
        ],
        borderColor: [
          '#dc2626',
          '#16a34a',
          '#2563eb',
          '#d97706',
        ],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${context.label}: ${context.parsed}%`;
          },
        },
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Distribution</h3>
      <div className="h-64">
        <Doughnut data={data} options={options} />
      </div>
    </div>
  );
};

export default SentimentChart;