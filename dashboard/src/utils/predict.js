const TRAFFIC_MAP  = { Low: 0, Medium: 8, High: 15, Jam: 25 };
const WEATHER_MAP  = { Sunny: 0, Cloudy: 3, Windy: 5, Fog: 8, Sandstorms: 12, Stormy: 15 };
const VEHICLE_MAP  = { Motorcycle: 0, Scooter: 2, 'Electric Scooter': 4, Bicycle: 9 };
const CITY_MAP     = { Metropolitian: 5, Urban: 0, 'Semi-Urban': -3 };
const ORDER_MAP    = { Snack: 0, Drinks: 1, Meal: 3, Buffet: 6 };

export function computePrediction(inp) {
  const isPeak      = (inp.hour >= 11 && inp.hour <= 14) || (inp.hour >= 18 && inp.hour <= 21);
  const isBadWeather = ['Fog', 'Sandstorms', 'Stormy'].includes(inp.weather);
  const distBucket  = inp.distance < 5 ? 'Short <5 km' : inp.distance <= 15 ? 'Medium 5–15 km' : 'Long >15 km';

  const parts = [
    { label: 'Distance',        value: +(inp.distance * 3.2).toFixed(1) },
    { label: 'Traffic',         value: TRAFFIC_MAP[inp.traffic]  ?? 0 },
    { label: 'Weather',         value: WEATHER_MAP[inp.weather]  ?? 0 },
    { label: 'Driver Rating',   value: +(-(inp.rating - 3) * 2.5).toFixed(1) },
    { label: 'Vehicle Type',    value: VEHICLE_MAP[inp.vehicleType] ?? 0 },
    { label: 'Veh. Condition',  value: +((3 - inp.vehicleCondition) * 1.8).toFixed(1) },
    { label: 'Festival',        value: inp.festival ? 12 : 0 },
    { label: 'City Type',       value: CITY_MAP[inp.city] ?? 0 },
    { label: 'Multi-Delivery',  value: +(inp.multipleDeliveries * 5.5).toFixed(1) },
    { label: 'Order Type',      value: ORDER_MAP[inp.orderType] ?? 0 },
    { label: 'Peak Hour',       value: isPeak ? 7 : 0 },
  ];

  const raw = parts.reduce((s, p) => s + p.value, 0);
  const prediction = Math.max(8, Math.min(90, raw));

  const contributions = parts
    .filter(p => p.value !== 0)
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 7);

  return { prediction, isPeak, isBadWeather, distBucket, contributions };
}
