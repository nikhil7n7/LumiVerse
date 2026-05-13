import React from 'react';
import { computeKitchenSync } from '../utils/kitchenPredict';

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

export default function KitchenPanel({ inputs, updateInput }) {
  const syncData = computeKitchenSync(inputs);
  const hourLabel = `${String(inputs.hour).padStart(2, '0')}:00`;
  
  let statusColor = 'text-[#22c55e] border-[#15803d]/40 bg-[#14532d]/30'; // Optimal
  if (syncData.action === 'HOLD TICKET') statusColor = 'text-[#f59e0b] border-[#d97706]/40 bg-[#92400e]/30'; // Hold
  else if (syncData.action === 'RUSH ORDER') statusColor = 'text-[#ef4444] border-[#991b1b]/40 bg-[#7f1d1d]/30'; // Rush

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 w-full">
      {/* Kitchen Inputs Panel */}
      <div className="bg-[#111111] border border-[#252525] rounded-lg flex flex-col">
        <div className="border-b border-[#252525] px-5 py-3 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#f59e0b]" />
          <span className="font-mono text-[11px] text-[#9ca3af] uppercase tracking-widest">Kitchen Variables</span>
        </div>

        <div className="p-5 space-y-6">
          <SelectRow label="Order Type" value={inputs.orderType}
            options={['Snack', 'Meal', 'Drinks', 'Buffet']}
            onChange={(v) => updateInput('orderType', v)} />
          
          <SliderRow label="Hour of Order" min={0} max={23} value={inputs.hour}
            valueLabel={hourLabel} onChange={(v) => updateInput('hour', v)} />
            
          <ToggleRow label="Festival Active" value={inputs.festival}
            onChange={(v) => updateInput('festival', v)} />
            
          <div className="border-t border-[#252525] pt-4 mt-2">
            <span className="text-[10px] font-mono text-[#4b5563] uppercase tracking-widest mb-3 block">Driver Delay Factors</span>
            <div className="grid grid-cols-2 gap-4">
              <SelectRow label="Traffic" value={inputs.traffic}
                options={['Low', 'Medium', 'High', 'Jam']}
                onChange={(v) => updateInput('traffic', v)} />
              <SelectRow label="Weather" value={inputs.weather}
                options={['Sunny', 'Cloudy', 'Windy', 'Fog', 'Sandstorms', 'Stormy']}
                onChange={(v) => updateInput('weather', v)} />
            </div>
          </div>
        </div>
      </div>

      {/* Sync Output Panel */}
      <div className="bg-[#111111] border border-[#252525] rounded-lg flex flex-col">
        <div className="border-b border-[#252525] px-5 py-3 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#3b82f6]" />
          <span className="font-mono text-[11px] text-[#9ca3af] uppercase tracking-widest">Kitchen Sync Output</span>
        </div>

        <div className="p-5 flex flex-col gap-6">
          {/* Main Action Banner */}
          <div className={`p-4 rounded border flex flex-col items-center justify-center gap-2 text-center ${statusColor}`}>
            <span className="font-mono text-sm tracking-widest uppercase opacity-80">{syncData.riskLevel}</span>
            <span className="font-mono text-2xl font-bold tracking-tight">{syncData.action}</span>
            {syncData.holdMinutes > 0 && (
              <span className="text-sm font-medium">Wait {syncData.holdMinutes} minutes before cooking to prevent cold food.</span>
            )}
            {syncData.driverWait > 0 && (
              <span className="text-sm font-medium">Driver will be waiting {syncData.driverWait} minutes for this order!</span>
            )}
            {syncData.holdMinutes === 0 && syncData.driverWait === 0 && (
              <span className="text-sm font-medium">Perfect timing. Fire the ticket now.</span>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#181818] border border-[#252525] rounded p-4 flex flex-col items-center justify-center text-center">
              <span className="text-[#9ca3af] font-mono text-[10px] uppercase tracking-widest mb-2">Est. Prep Time</span>
              <div className="flex items-baseline gap-1">
                <span className="font-mono text-4xl font-bold text-[#f59e0b]">{syncData.prepTime}</span>
                <span className="font-mono text-sm text-[#4b5563]">min</span>
              </div>
              {syncData.isPeak && <span className="text-[10px] text-[#ef4444] font-mono mt-1">+ PEAK RUSH</span>}
            </div>

            <div className="bg-[#181818] border border-[#252525] rounded p-4 flex flex-col items-center justify-center text-center">
              <span className="text-[#9ca3af] font-mono text-[10px] uppercase tracking-widest mb-2">Driver Arrival</span>
              <div className="flex items-baseline gap-1">
                <span className="font-mono text-4xl font-bold text-[#3b82f6]">{syncData.driverArrivalTime}</span>
                <span className="font-mono text-sm text-[#4b5563]">min</span>
              </div>
            </div>
          </div>
          
          <div className="mt-auto pt-4 border-t border-[#252525]">
            <p className="text-[11px] text-[#6b7280] leading-relaxed">
              <strong>How this works:</strong> We estimate driver arrival time based on current traffic/weather, and compare it to standard preparation times (adjusted for peak hours and festivals). The system recommends when to start cooking so food is handed to the driver freshly packed.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
