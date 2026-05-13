const STATS = [
  { label: 'R² Score',      value: '0.83',    unit: '',     note: 'Variance explained by model' },
  { label: 'MAE',           value: '3.02',    unit: ' min', note: 'Mean absolute error' },
  { label: 'RMSE',          value: '3.76',    unit: ' min', note: 'Root mean squared error' },
  { label: 'Training Set',  value: '43,423',  unit: '',     note: 'Delivery records trained on' },
];

export default function MetricsStrip() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {STATS.map((s) => (
        <div
          key={s.label}
          className="bg-[#111111] border border-[#252525] rounded p-4 flex flex-col gap-1 hover:border-[#f59e0b]/40 transition-colors"
        >
          <span className="text-[#4b5563] font-mono text-[10px] uppercase tracking-widest">{s.label}</span>
          <div className="flex items-baseline gap-1">
            <span className="font-mono text-2xl font-bold text-[#f59e0b]">{s.value}</span>
            {s.unit && <span className="font-mono text-sm text-[#9ca3af]">{s.unit}</span>}
          </div>
          <span className="text-[#4b5563] text-[11px]">{s.note}</span>
        </div>
      ))}
    </div>
  );
}
