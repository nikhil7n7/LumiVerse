export default function Header({ activeTab, onTabChange }) {
  return (
    <header className="sticky top-0 z-50 border-b border-[#252525] bg-[#0a0a0a]/95 backdrop-blur-sm">
      <div className="max-w-[1400px] mx-auto px-5 h-14 flex items-center justify-between">
        {/* Left: brand */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-[#f59e0b] text-lg font-bold tracking-widest font-mono">▶</span>
            <span className="text-white font-bold text-lg tracking-tight">DelivR</span>
            <span className="text-[#f59e0b] font-bold text-lg tracking-tight">Intelligence</span>
          </div>
          <div className="hidden sm:block h-4 w-px bg-[#252525]" />
          <span className="hidden sm:block text-[#4b5563] font-mono text-[11px] tracking-wider">
            XGBoost · 43,423 deliveries · R² 0.83
          </span>
        </div>

        {/* Center: Tabs */}
        <div className="hidden md:flex items-center bg-[#111111] border border-[#252525] rounded p-1">
          <button 
            onClick={() => onTabChange('dispatch')}
            className={`px-4 py-1 text-xs font-mono tracking-widest rounded transition-colors ${activeTab === 'dispatch' ? 'bg-[#252525] text-white' : 'text-[#6b7280] hover:text-[#9ca3af]'}`}
          >
            DISPATCH
          </button>
          <button 
            onClick={() => onTabChange('kitchen')}
            className={`px-4 py-1 text-xs font-mono tracking-widest rounded transition-colors ${activeTab === 'kitchen' ? 'bg-[#252525] text-white' : 'text-[#6b7280] hover:text-[#9ca3af]'}`}
          >
            KITCHEN OPS
          </button>
          <button 
            onClick={() => onTabChange('eda')}
            className={`px-4 py-1 text-xs font-mono tracking-widest rounded transition-colors ${activeTab === 'eda' ? 'bg-[#252525] text-white' : 'text-[#6b7280] hover:text-[#9ca3af]'}`}
          >
            EDA INSIGHTS
          </button>
        </div>

        {/* Right: status */}
        <div className="flex items-center gap-2.5 border border-[#252525] rounded px-3 py-1.5 bg-[#111111]">
          <div className="w-2 h-2 rounded-full bg-[#22c55e] pulse-dot" />
          <span className="font-mono text-[11px] text-[#22c55e] tracking-widest uppercase">
            Model Live
          </span>
        </div>
      </div>
    </header>
  );
}
