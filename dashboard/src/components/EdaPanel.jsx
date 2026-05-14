export default function EdaPanel() {
  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="bg-[#111111] border border-[#252525] rounded-lg overflow-hidden">
        <div className="border-b border-[#252525] px-5 py-3 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#ec4899]" />
          <span className="font-mono text-[11px] text-[#9ca3af] uppercase tracking-widest">Exploratory Data Analysis</span>
          <span className="ml-auto font-mono text-[10px] text-[#4b5563]">PEARSON CORRELATION</span>
        </div>
        
        <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-[#0d0d0d] border border-[#252525] rounded p-2 flex items-center justify-center">
            <img 
              src="/eda_correlation_heatmap.png" 
              alt="EDA Correlation Heatmap" 
              className="max-w-full h-auto rounded"
            />
          </div>
          
          <div className="flex flex-col gap-6">
            <div>
              <h3 className="text-[#ec4899] font-mono text-sm uppercase tracking-widest mb-3">Key Insights</h3>
              <p className="text-[#9ca3af] text-sm leading-relaxed">
                This heatmap displays the Pearson correlation coefficients between the engineered features and the target variable <code className="text-[#f59e0b] bg-[#1a1a1a] px-1 py-0.5 rounded text-xs">Time_taken (min)</code>.
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="bg-[#181818] border border-[#252525] p-4 rounded">
                <span className="text-[#f59e0b] font-mono text-[11px] uppercase tracking-widest block mb-1">Strongest Predictors</span>
                <p className="text-[#d1d5db] text-xs leading-relaxed">
                  Notice the dark red intersections for <strong className="text-white">Distance_km</strong> and <strong className="text-white">Road_traffic_density</strong>. These are mathematically proven to be the primary drivers of delivery delays.
                </p>
              </div>
              
              <div className="bg-[#181818] border border-[#252525] p-4 rounded">
                <span className="text-[#3b82f6] font-mono text-[11px] uppercase tracking-widest block mb-1">Negative Correlations</span>
                <p className="text-[#d1d5db] text-xs leading-relaxed">
                  The dark blue squares, such as <strong className="text-white">Vehicle_condition</strong>, show an inverse relationship. A higher condition score results in a lower delivery time.
                </p>
              </div>
              
              <div className="bg-[#181818] border border-[#252525] p-4 rounded">
                <span className="text-[#22c55e] font-mono text-[11px] uppercase tracking-widest block mb-1">Collinearity Check</span>
                <p className="text-[#d1d5db] text-xs leading-relaxed">
                  We use this matrix to ensure no two input features are perfectly correlated with each other, which would cause model confusion (multicollinearity).
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
