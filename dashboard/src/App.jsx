import { useState, useMemo } from 'react';
import Header from './components/Header';
import MetricsStrip from './components/MetricsStrip';
import InputPanel from './components/InputPanel';
import PredictionPanel from './components/PredictionPanel';
import FeatureImportanceChart from './components/FeatureImportanceChart';
import KitchenPanel from './components/KitchenPanel';
import { computePrediction } from './utils/predict';

const DEFAULT = {
  distance: 8,
  rating: 4.2,
  vehicleCondition: 2,
  multipleDeliveries: 0,
  traffic: 'Medium',
  weather: 'Sunny',
  orderType: 'Meal',
  vehicleType: 'Motorcycle',
  festival: false,
  city: 'Urban',
  hour: 12,
};

export default function App() {
  const [inputs, setInputs]       = useState(DEFAULT);
  const [isLoading, setIsLoading] = useState(false);
  const [showResult, setShow]     = useState(true);
  const [activeTab, setActiveTab] = useState('dispatch');

  const result = useMemo(() => computePrediction(inputs), [inputs]);

  const update = (key, val) => setInputs((p) => ({ ...p, [key]: val }));

  const handlePredict = () => {
    setIsLoading(true);
    setShow(false);
    setTimeout(() => { setIsLoading(false); setShow(true); }, 800);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-100 font-sans">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="max-w-[1400px] mx-auto px-4 py-6 space-y-5">
        <MetricsStrip />
        
        {activeTab === 'dispatch' ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <InputPanel inputs={inputs} updateInput={update} result={result} onPredict={handlePredict} />
              <PredictionPanel result={result} isLoading={isLoading} showResult={showResult} />
            </div>
            <FeatureImportanceChart />
          </>
        ) : (
          <KitchenPanel inputs={inputs} updateInput={update} />
        )}

        <p className="text-center font-mono text-[10px] text-[#2a2a2a] pb-4 tracking-widest mt-8">
          DELIVR INTELLIGENCE · XGBOOST REGRESSOR · MAE 3.02 MIN · R² 0.83
        </p>
      </main>
    </div>
  );
}
