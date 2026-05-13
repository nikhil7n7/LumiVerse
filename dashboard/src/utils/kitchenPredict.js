import { computePrediction } from './predict';

const PREP_BASE = { Snack: 5, Drinks: 3, Meal: 12, Buffet: 25 };

export function computeKitchenSync(inp) {
  // 1. Calculate Driver Arrival Time (How long until driver gets here)
  // We use the delivery prediction logic, but ignore distance (assume driver is nearby or en route)
  // For simplicity in this dashboard, we'll estimate driver arrival using a simplified formula
  
  // We'll reuse the prediction logic to get a sense of road conditions
  const deliveryResult = computePrediction(inp);
  
  // Let's say driver arrival depends on traffic and weather, base 10 mins
  const trafficDelay = { Low: 0, Medium: 5, High: 10, Jam: 18 }[inp.traffic] || 0;
  const weatherDelay = { Sunny: 0, Cloudy: 2, Windy: 4, Fog: 7, Sandstorms: 10, Stormy: 12 }[inp.weather] || 0;
  
  const driverArrivalTime = 8 + trafficDelay + weatherDelay;
  
  // 2. Calculate Kitchen Prep Time
  let prepTime = PREP_BASE[inp.orderType] || 10;
  
  const isPeak = (inp.hour >= 11 && inp.hour <= 14) || (inp.hour >= 18 && inp.hour <= 21);
  if (isPeak) prepTime *= 1.4; // 40% slower during peak
  if (inp.festival) prepTime *= 1.6; // 60% slower during festivals
  
  prepTime = Math.round(prepTime);
  
  // 3. The Sync Logic
  // If driver arrives in 20 mins, but food takes 5 mins, we should HOLD cooking for 15 mins.
  // If driver arrives in 5 mins, but food takes 15 mins, driver will WAIT 10 mins.
  
  const syncDiff = driverArrivalTime - prepTime;
  
  let action = '';
  let riskLevel = '';
  let holdMinutes = 0;
  let driverWait = 0;
  
  if (syncDiff > 5) {
    // Driver arrives way later than food is ready = COLD FOOD
    action = 'HOLD TICKET';
    riskLevel = 'Cold Food Risk';
    holdMinutes = syncDiff - 2; // Start 2 mins before driver arrives
  } else if (syncDiff < -5) {
    // Driver arrives way before food is ready = DRIVER WAITING (ANGRY)
    action = 'RUSH ORDER';
    riskLevel = 'Driver Wait Risk';
    driverWait = Math.abs(syncDiff);
  } else {
    // Perfect sync (+/- 5 mins)
    action = 'START COOKING NOW';
    riskLevel = 'Optimal Sync';
  }

  return {
    prepTime,
    driverArrivalTime,
    action,
    riskLevel,
    holdMinutes,
    driverWait,
    isPeak
  };
}
