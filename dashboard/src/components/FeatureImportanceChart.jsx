import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const FEATURES = [
  { label: 'Distance_km',            pct: 28 },
  { label: 'Road_traffic_density',   pct: 22 },
  { label: 'is_peak_hour',           pct: 12 },
  { label: 'is_bad_weather',         pct: 10 },
  { label: 'Delivery_person_Ratings',pct: 9  },
  { label: 'multiple_deliveries',    pct: 7  },
  { label: 'Festival',               pct: 6  },
  { label: 'Vehicle_condition',      pct: 6  },
];

const PALETTE = [
  '#f59e0b', '#ea580c', '#f97316', '#d97706',
  '#b45309', '#92400e', '#78350f', '#451a03',
];

export default function FeatureImportanceChart() {
  const sorted = [...FEATURES].sort((a, b) => a.pct - b.pct);

  const data = {
    labels: sorted.map((f) => f.label),
    datasets: [{
      label: 'Importance (%)',
      data: sorted.map((f) => f.pct),
      backgroundColor: sorted.map((_, i) => PALETTE[i] + 'cc'),
      borderColor:     sorted.map((_, i) => PALETTE[i]),
      borderWidth: 1,
      borderRadius: 3,
    }],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => ` ${ctx.parsed.x}% importance`,
        },
        backgroundColor: '#1a1a1a',
        borderColor: '#252525',
        borderWidth: 1,
        titleColor: '#9ca3af',
        bodyColor: '#f59e0b',
        titleFont: { family: "'JetBrains Mono', monospace", size: 11 },
        bodyFont:  { family: "'JetBrains Mono', monospace", size: 12 },
      },
    },
    scales: {
      x: {
        grid:  { color: '#1f1f1f', drawBorder: false },
        ticks: {
          color: '#4b5563',
          font:  { family: "'JetBrains Mono', monospace", size: 10 },
          callback: (v) => `${v}%`,
        },
        border: { color: '#252525' },
      },
      y: {
        grid:  { display: false },
        ticks: {
          color: '#9ca3af',
          font:  { family: "'JetBrains Mono', monospace", size: 11 },
        },
        border: { color: '#252525' },
      },
    },
  };

  return (
    <div className="bg-[#111111] border border-[#252525] rounded-lg">
      <div className="border-b border-[#252525] px-5 py-3 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-[#f59e0b]" />
        <span className="font-mono text-[11px] text-[#9ca3af] uppercase tracking-widest">
          Feature Importance — XGBoost Global
        </span>
        <span className="ml-auto font-mono text-[10px] text-[#4b5563]">TOP 8 FEATURES</span>
      </div>
      <div className="p-5" style={{ height: 280 }}>
        <Bar data={data} options={options} />
      </div>
    </div>
  );
}
