function SliderRow({ label, value, min, max, step = 1, unit = '', onChange, valueLabel }) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-center">
        <span className="text-[#9ca3af] text-[11px] font-mono uppercase tracking-wider">{label}</span>
        <span className="text-[#f59e0b] font-mono text-sm font-semibold">
          {valueLabel ?? value}{unit}
        </span>
      </div>
      <input
        type="range" min={min} max={max} step={step}
        value={value}
        onChange={(e) => onChange(step < 1 ? parseFloat(e.target.value) : parseInt(e.target.value))}
      />
    </div>
  );
}

function SelectRow({ label, value, options, onChange }) {
  return (
    <div className="space-y-1.5">
      <span className="text-[#9ca3af] text-[11px] font-mono uppercase tracking-wider block">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function ToggleRow({ label, value, onChange }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-[#9ca3af] text-[11px] font-mono uppercase tracking-wider">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-[11px] text-[#4b5563]">{value ? 'YES' : 'NO'}</span>
        <div className={`toggle-track ${value ? 'on' : ''}`} onClick={() => onChange(!value)}>
          <div className="toggle-thumb" />
        </div>
      </div>
    </div>
  );
}

function Badge({ label, value, color = 'amber' }) {
  const colors = {
    amber: 'bg-[#92400e]/40 text-[#f59e0b] border-[#d97706]/40',
    green: 'bg-[#14532d]/40 text-[#22c55e] border-[#15803d]/40',
    red:   'bg-[#7f1d1d]/40 text-[#f87171] border-[#991b1b]/40',
    gray:  'bg-[#1f2937]/40 text-[#9ca3af] border-[#374151]/40',
  };
  return (
    <div className="space-y-1.5">
      <span className="text-[#9ca3af] text-[11px] font-mono uppercase tracking-wider block">{label}</span>
      <div className={`inline-flex items-center px-2.5 py-1 rounded border font-mono text-[11px] tracking-wider ${colors[color]}`}>
        {value}
      </div>
    </div>
  );
}

export default function InputPanel({ inputs, updateInput, result, onPredict }) {
  const hourLabel = `${String(inputs.hour).padStart(2, '0')}:00`;
  const peakColor  = result.isPeak ? 'amber' : 'gray';
  const badWxColor = result.isBadWeather ? 'red' : 'gray';

  return (
    <div className="bg-[#111111] border border-[#252525] rounded-lg flex flex-col">
      {/* Panel header */}
      <div className="border-b border-[#252525] px-5 py-3 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-[#f59e0b]" />
        <span className="font-mono text-[11px] text-[#9ca3af] uppercase tracking-widest">Input Parameters</span>
        <span className="ml-auto font-mono text-[10px] text-[#4b5563]">14 FEATURES</span>
      </div>

      <div className="p-5 space-y-5 flex-1">
        {/* Grid: 2 columns */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-5">
          <SliderRow label="Distance" min={1} max={50} value={inputs.distance}
            unit=" km" onChange={(v) => updateInput('distance', v)} />
          <SliderRow label="Driver Rating" min={1.0} max={5.0} step={0.1} value={inputs.rating}
            unit=" ★" onChange={(v) => updateInput('rating', v)} />
          <SliderRow label="Vehicle Condition" min={0} max={3} value={inputs.vehicleCondition}
            onChange={(v) => updateInput('vehicleCondition', v)} />
          <SliderRow label="Multiple Deliveries" min={0} max={3} value={inputs.multipleDeliveries}
            onChange={(v) => updateInput('multipleDeliveries', v)} />
          <SliderRow label="Hour of Order" min={0} max={23} value={inputs.hour}
            valueLabel={hourLabel} onChange={(v) => updateInput('hour', v)} />

          <SelectRow label="Traffic Density" value={inputs.traffic}
            options={['Low', 'Medium', 'High', 'Jam']}
            onChange={(v) => updateInput('traffic', v)} />
          <SelectRow label="Weather" value={inputs.weather}
            options={['Sunny', 'Cloudy', 'Windy', 'Fog', 'Sandstorms', 'Stormy']}
            onChange={(v) => updateInput('weather', v)} />
          <SelectRow label="Order Type" value={inputs.orderType}
            options={['Snack', 'Meal', 'Drinks', 'Buffet']}
            onChange={(v) => updateInput('orderType', v)} />
          <SelectRow label="Vehicle Type" value={inputs.vehicleType}
            options={['Motorcycle', 'Scooter', 'Electric Scooter', 'Bicycle']}
            onChange={(v) => updateInput('vehicleType', v)} />
          <SelectRow label="City" value={inputs.city}
            options={['Metropolitian', 'Urban', 'Semi-Urban']}
            onChange={(v) => updateInput('city', v)} />

          <div className="sm:col-span-2">
            <ToggleRow label="Festival Active" value={inputs.festival}
              onChange={(v) => updateInput('festival', v)} />
          </div>
        </div>

        {/* Derived badges */}
        <div className="border-t border-[#252525] pt-4">
          <p className="text-[10px] font-mono text-[#4b5563] uppercase tracking-widest mb-3">Auto-Derived Features</p>
          <div className="grid grid-cols-3 gap-3">
            <Badge label="Dist Bucket" value={result.distBucket.split(' ')[0]} color="amber" />
            <Badge label="Peak Hour" value={result.isPeak ? '▲ PEAK' : '— OFF-PEAK'} color={peakColor} />
            <Badge label="Bad Weather" value={result.isBadWeather ? '⚠ BAD' : '✓ CLEAR'} color={badWxColor} />
          </div>
        </div>
      </div>

      {/* Predict button */}
      <div className="border-t border-[#252525] p-5">
        <button className="predict-btn" onClick={onPredict}>
          ⚡ Run Prediction
        </button>
      </div>
    </div>
  );
}
