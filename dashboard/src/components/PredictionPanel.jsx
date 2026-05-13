import { useEffect, useRef, useState } from 'react';

function useCountUp(target, duration = 500) {
  const [display, setDisplay] = useState(target);
  const prev = useRef(target);

  useEffect(() => {
    const start = prev.current;
    const diff  = target - start;
    const t0    = performance.now();
    let raf;
    const tick  = (now) => {
      const p = Math.min((now - t0) / duration, 1);
      const e = 1 - Math.pow(1 - p, 3); // ease-out cubic
      setDisplay(+(start + diff * e).toFixed(1));
      if (p < 1) raf = requestAnimationFrame(tick);
      else prev.current = target;
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);

  return display;
}

function StatusBadge({ minutes }) {
  if (minutes < 20) return (
    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded border border-[#15803d]/60 bg-[#14532d]/30">
      <span className="w-1.5 h-1.5 rounded-full bg-[#22c55e] animate-pulse" />
      <span className="font-mono text-sm text-[#22c55e] tracking-widest uppercase">Fast</span>
    </div>
  );
  if (minutes <= 40) return (
    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded border border-[#d97706]/60 bg-[#92400e]/30">
      <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b] animate-pulse" />
      <span className="font-mono text-sm text-[#f59e0b] tracking-widest uppercase">On Time</span>
    </div>
  );
  return (
    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded border border-[#991b1b]/60 bg-[#7f1d1d]/30">
      <span className="w-1.5 h-1.5 rounded-full bg-[#ef4444] animate-pulse" />
      <span className="font-mono text-sm text-[#ef4444] tracking-widest uppercase">Delayed</span>
    </div>
  );
}

function ContribChart({ contributions }) {
  const maxAbs = Math.max(...contributions.map((c) => Math.abs(c.value)), 1);
  return (
    <div className="space-y-2.5">
      {contributions.map((c) => {
        const pct   = (Math.abs(c.value) / maxAbs) * 100;
        const isPos = c.value > 0;
        return (
          <div key={c.label} className="flex items-center gap-2">
            <span className="w-28 text-[11px] font-mono text-[#6b7280] shrink-0 text-right pr-1">
              {c.label}
            </span>
            <div className="flex-1 flex items-center gap-1.5">
              {isPos ? (
                <>
                  <div className="w-1/2 flex justify-end">
                    <div style={{ width: `${pct / 2}%` }} className="h-3.5 contrib-bar-pos" />
                  </div>
                  <div className="w-1/2" />
                </>
              ) : (
                <>
                  <div className="w-1/2" />
                  <div className="w-1/2">
                    <div style={{ width: `${pct / 2}%` }} className="h-3.5 contrib-bar-neg" />
                  </div>
                </>
              )}
            </div>
            <span className={`w-12 text-right text-[11px] font-mono shrink-0 ${isPos ? 'text-[#f59e0b]' : 'text-[#22c55e]'}`}>
              {isPos ? '+' : ''}{c.value}m
            </span>
          </div>
        );
      })}
      {/* Centre line */}
      <div className="relative">
        <div className="absolute left-1/2 -top-full bottom-0 w-px bg-[#252525] -translate-x-1/2 pointer-events-none" style={{ top: `-${contributions.length * 28}px` }} />
      </div>
    </div>
  );
}

export default function PredictionPanel({ result, isLoading, showResult }) {
  const animated = useCountUp(result.prediction);
  const whole    = Math.round(animated);

  return (
    <div className="bg-[#111111] border border-[#252525] rounded-lg flex flex-col">
      {/* Panel header */}
      <div className="border-b border-[#252525] px-5 py-3 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-[#22c55e]" />
        <span className="font-mono text-[11px] text-[#9ca3af] uppercase tracking-widest">Prediction Output</span>
        <span className="ml-auto font-mono text-[10px] text-[#4b5563]">LIVE · AUTO-UPDATES</span>
      </div>

      {/* Hero prediction */}
      <div className="relative flex flex-col items-center justify-center py-10 px-6 border-b border-[#252525] bg-[#0d0d0d] grid-bg overflow-hidden">
        <div className="scanlines absolute inset-0" />

        {isLoading ? (
          <div className="flex flex-col items-center gap-4 py-4">
            <svg className="spinner w-10 h-10 text-[#f59e0b]" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
              <path className="opacity-80" d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
            </svg>
            <span className="font-mono text-[#4b5563] text-sm tracking-widest">COMPUTING...</span>
          </div>
        ) : (
          <div className="relative flex flex-col items-center gap-3">
            <div className="flex items-end gap-2">
              <span className="font-mono font-bold text-[88px] leading-none text-white num-display">
                {whole}
              </span>
              <span className="font-mono text-3xl text-[#9ca3af] mb-3">min</span>
            </div>
            <span className="font-mono text-[12px] text-[#4b5563] tracking-wider">
              ±3.76 min confidence band
            </span>
            <StatusBadge minutes={result.prediction} />
          </div>
        )}
      </div>

      {/* Contribution chart */}
      {showResult && !isLoading && (
        <div className="p-5 flex-1">
          <div className="flex items-center justify-between mb-4">
            <span className="font-mono text-[10px] text-[#4b5563] uppercase tracking-widest">
              Feature Contributions
            </span>
            <div className="flex gap-3 text-[10px] font-mono">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-[#f59e0b]" />Delay</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-[#22c55e]" />Saves</span>
            </div>
          </div>
          <ContribChart contributions={result.contributions} />
        </div>
      )}
    </div>
  );
}
