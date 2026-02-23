import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { motion, AnimatePresence } from 'framer-motion';
import { Droplet, AlertTriangle, Truck, MapPin, Activity, CheckCircle2, ChevronRight, X } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

// Leaflet icon fix for React
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow
});
L.Marker.prototype.options.icon = DefaultIcon;

// Custom Map Controller to smoothly "fly" to selected village and handle resizing
function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, {
      duration: 1.5,
      easeLinearity: 0.25
    });
  }, [center, zoom, map]);

  // Fix for Leaflet tile loading glitch (gray map area problem)
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 250);
    return () => clearTimeout(timer);
  }, [map]);

  return null;
}

function App() {
  const [dashboardData, setDashboardData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('critical');
  const [selectedVillage, setSelectedVillage] = useState(null);
  const [availableTankers, setAvailableTankers] = useState(0);

  // Default India Center
  const defaultCenter = [22.5937, 78.9629];

  useEffect(() => {
    // Fetch data from FastAPI backend
    const fetchData = async () => {
      try {
        const [dashRes, tankerRes] = await Promise.all([
          axios.get('http://127.0.0.1:8000/crisis-dashboard/?threshold=0.0'),
          axios.get('http://127.0.0.1:8000/tankers/available')
        ]);
        setDashboardData(dashRes.data);
        setAvailableTankers(tankerRes.data.available);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    const handleDispatch = async (villageId) => {
      try {
        await axios.post(`http://127.0.0.1:8000/dispatch-tanker/${villageId}`);
        // Refresh data rapidly
        const tankerRes = await axios.get('http://127.0.0.1:8000/tankers/available');
        setAvailableTankers(tankerRes.data.available);
        alert('Tanker Dispatched Successfully to ' + selectedVillage.village_name + '!');
      } catch (error) {
        alert(error.response?.data?.detail || 'No tankers available!');
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getMarkerColor = (stress) => {
    if (stress >= 8.0) return '#ef4444'; // Red - Critical
    if (stress >= 5.0) return '#f59e0b'; // Amber - Warning
    return '#10b981'; // Emerald - Safe
  };

  const getFilteredData = () => {
    let sorted = [...dashboardData].sort((a, b) => b.stress_index - a.stress_index);
    if (activeTab === 'critical') return sorted.filter(v => v.stress_index >= 8.0);
    if (activeTab === 'warning') return sorted.filter(v => v.stress_index >= 5.0 && v.stress_index < 8.0);
    return sorted; // 'all'
  };

  const mapCenter = selectedVillage
    ? [selectedVillage.location.lat, selectedVillage.location.lng]
    : defaultCenter;

  // Zoom out to 5 for national view by default
  const mapZoom = selectedVillage ? 14 : 5;

  return (
    <div className="flex h-screen w-full bg-[#0f172a] font-sans overflow-hidden">

      {/* Floating Header */}
      <motion.div
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="absolute top-6 left-6 z-30 flex items-center gap-4 bg-white/10 backdrop-blur-md border border-white/20 p-3 pr-6 rounded-2xl shadow-2xl"
      >
        <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg">
          <Activity className="text-white" size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white drop-shadow-md">Drought Engine AI</h1>
          <p className="text-blue-200 text-xs font-semibold tracking-widest uppercase mt-0.5">National Command Center</p>
        </div>
      </motion.div>

      {/* Map Area (Full Screen Background) */}
      <div className="absolute inset-0 z-0 h-screen w-full">
        <MapContainer
          center={defaultCenter}
          zoom={5}
          zoomControl={false}
          style={{ height: "100vh", width: "100%" }}
          className="w-full h-full"
        >
          <MapController center={mapCenter} zoom={mapZoom} />

          {/* Standard OpenStreetMap for reliable loading */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
            className="map-tiles"
          />

          {dashboardData.map((village) => (
            <CircleMarker
              key={village.village_id}
              center={[village.location.lat, village.location.lng]}
              radius={village.stress_index >= 8.0 ? 16 : village.stress_index >= 5.0 ? 10 : 6}
              fillColor={getMarkerColor(village.stress_index)}
              fillOpacity={village.stress_index >= 8.0 ? 0.4 : 0.6}
              color={getMarkerColor(village.stress_index)}
              weight={village.stress_index >= 8.0 ? 2 : 1}
              className={`${village.stress_index >= 8.0 ? 'animate-pulse' : ''} cursor-pointer`}
              eventHandlers={{
                click: () => setSelectedVillage(village)
              }}
            >
              {village.stress_index >= 8.0 && (
                <CircleMarker
                  center={[village.location.lat, village.location.lng]}
                  radius={4}
                  fillColor="#ef4444"
                  fillOpacity={1}
                  color="#ffffff"
                  weight={2}
                />
              )}
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* Dynamic Side/Bottom Panel Area */}
      <div className="absolute inset-0 z-20 pointer-events-none flex flex-col justify-end">

        {/* Bottom Scrolling Carousel for Cities */}
        <div className="w-full pointer-events-auto bg-gradient-to-t from-slate-900/95 via-slate-900/80 to-transparent pb-6 pt-24 px-8 backdrop-blur-sm">

          {/* Tabs & Stats Header inside the bottom tray */}
          <div className="flex justify-between items-end mb-6">
            <div className="flex gap-2">
              {['all', 'critical', 'warning'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-5 py-2 rounded-full text-sm font-bold capitalize transition-all ${activeTab === tab
                    ? 'bg-blue-600 text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]'
                    : 'bg-white/10 text-slate-300 hover:bg-white/20'
                    }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            <div className="flex gap-4">
              <div className="bg-white/10 border border-white/10 rounded-xl px-4 py-2 flex items-center gap-3 backdrop-blur-md">
                <AlertTriangle className="text-red-400" size={20} />
                <div>
                  <p className="text-xs text-slate-400 font-semibold uppercase">Critical</p>
                  <p className="text-lg font-bold text-white leading-none">
                    {dashboardData.filter(v => v.stress_index >= 8.0).length}
                  </p>
                </div>
              </div>
              <div className="bg-white/10 border border-white/10 rounded-xl px-4 py-2 flex items-center gap-3 backdrop-blur-md">
                <Truck className="text-blue-400" size={20} />
                <div>
                  <p className="text-xs text-slate-400 font-semibold uppercase">Tankers Deployable</p>
                  <p className="text-lg font-bold text-white leading-none">{availableTankers}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Horizontal Scrolling City Cards */}
          <div className="flex gap-6 overflow-x-auto pb-6 scrollbar-hide snap-x" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
            {loading ? (
              Array(5).fill(0).map((_, i) => (
                <div key={i} className="min-w-[320px] h-[180px] bg-white/5 rounded-2xl animate-pulse backdrop-blur-md border border-white/10"></div>
              ))
            ) : (
              getFilteredData().map((village) => {
                const isSelected = selectedVillage?.village_id === village.village_id;
                const isCritical = village.stress_index >= 8.0;

                return (
                  <motion.div
                    key={village.village_id}
                    layout
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, width: 0 }}
                    whileHover={{ y: -5 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedVillage(village)}
                    className={`min-w-[320px] shrink-0 snap-center cursor-pointer rounded-2xl p-5 border backdrop-blur-xl transition-all duration-300 
                          ${isSelected ? (isCritical ? 'border-red-500 border-2 bg-red-950/40 shadow-[0_0_30px_rgba(239,68,68,0.2)]' : 'border-blue-500 border-2 bg-blue-900/40') : 'border-white/10 bg-white/5 hover:bg-white/10'}
                        `}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                          {village.village_name}
                        </h3>
                        <p className="text-slate-400 text-xs font-semibold tracking-wider flex items-center gap-1 mt-1">
                          <MapPin size={12} /> {village.district} • Priority: {village.priority_score?.toFixed(1)}
                        </p>
                      </div>
                      <div className={`text-2xl font-black tabular-nums tracking-tighter ${isCritical ? 'text-red-400' : village.stress_index >= 5.0 ? 'text-amber-400' : 'text-emerald-400'
                        }`}>
                        {village.stress_index.toFixed(1)}
                      </div>
                    </div>

                    {/* Progress Mini-bar */}
                    <div className="h-1.5 w-full bg-slate-800 rounded-full mb-5 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(100, (village.stress_index / 10) * 100)}%` }}
                        className={`h-full rounded-full 
                               ${isCritical ? 'bg-red-500' : village.stress_index >= 5.0 ? 'bg-amber-500' : 'bg-emerald-500'}
                             `}
                      />
                    </div>

                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-400">Pop: <span className="text-white font-medium">{village.population.toLocaleString()}</span></span>
                      <span className="text-blue-400 font-semibold flex items-center gap-1 text-xs uppercase tracking-wider">
                        Analyze <ChevronRight size={14} />
                      </span>
                    </div>
                  </motion.div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Floating Detailed Inspection Panel (Appears when city is clicked) */}
      <AnimatePresence>
        {selectedVillage && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="absolute top-6 bottom-32 right-6 w-[380px] bg-slate-900/90 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-2xl z-40 overflow-hidden flex flex-col"
          >
            <div className="p-6 border-b border-white/10 relative">
              <button
                onClick={() => setSelectedVillage(null)}
                className="absolute top-4 right-4 p-2 bg-white/5 hover:bg-white/10 rounded-full text-slate-400 hover:text-white transition"
              >
                <X size={20} />
              </button>

              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-4 shadow-lg
                  ${selectedVillage.stress_index >= 8.0 ? 'bg-gradient-to-br from-red-500 to-red-600' : 'bg-gradient-to-br from-emerald-500 to-emerald-600'}
               `}>
                {selectedVillage.stress_index >= 8.0 ? <Droplet className="text-white" size={24} /> : <CheckCircle2 className="text-white" size={24} />}
              </div>

              <h2 className="text-3xl font-black text-white">{selectedVillage.village_name}</h2>
              <p className="text-slate-400 font-medium tracking-wide mt-1 flex items-center gap-2">
                <MapPin size={14} /> {selectedVillage.district} District
              </p>
            </div>

            <div className="flex-1 p-6 space-y-6 overflow-y-auto">

              {/* Premium Stress Gauge Component */}
              <div className="bg-black/20 rounded-2xl p-5 border border-white/5 relative overflow-hidden">
                {selectedVillage.stress_index >= 8.0 && (
                  <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/10 blur-3xl rounded-full translate-x-10 -translate-y-10" />
                )}
                <p className="text-slate-400 text-xs font-bold tracking-widest uppercase mb-2">AI Stress Evaluation</p>
                <div className="flex items-end gap-2 text-white">
                  <span className="text-6xl font-black tracking-tighter leading-none">{selectedVillage.stress_index.toFixed(1)}</span>
                  <span className="text-xl font-medium text-slate-500 mb-1">/ 10</span>
                </div>
              </div>

              <div className="bg-black/20 rounded-2xl p-5 border border-white/5 relative overflow-hidden">
                <p className="text-slate-400 text-xs font-bold tracking-widest uppercase mb-2">30-Day Forecast</p>
                <div className="flex items-center gap-3">
                  <span className={`text-3xl font-black ${selectedVillage.predicted_stress_index > selectedVillage.stress_index ? 'text-red-400' : 'text-emerald-400'}`}>
                    {selectedVillage.predicted_stress_index?.toFixed(1) || "N/A"}
                  </span>
                  <span className="text-sm font-medium text-slate-500">
                    {selectedVillage.predicted_stress_index > selectedVillage.stress_index ? "📈 Worsening" : "📉 Improving"}
                  </span>
                </div>
              </div>

              <div className="bg-black/20 rounded-2xl p-5 border border-white/5">
                <p className="text-slate-400 text-xs font-bold tracking-widest uppercase mb-4">Triage & Demographics</p>
                <div className="flex justify-between items-center mb-3">
                  <span className="text-slate-300">Total Population</span>
                  <strong className="text-white bg-white/10 px-3 py-1 rounded-lg">{selectedVillage.population.toLocaleString()}</strong>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-300">Triage Priority Score</span>
                  <strong className="text-amber-400 bg-amber-400/10 px-3 py-1 rounded-lg">{selectedVillage.priority_score?.toFixed(1) || "N/A"} / 100</strong>
                </div>
              </div>

              {selectedVillage.stress_index >= 8.0 && (
                <div className="mt-8">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleDispatch(selectedVillage.village_id)}
                    className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-red-500 to-rose-600 shadow-[0_0_20px_rgba(239,68,68,0.3)] text-white font-bold py-4 rounded-xl text-lg relative overflow-hidden group"
                  >
                    <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform" />
                    <Truck size={20} />
                    Force Dispatch Tanker
                  </motion.button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}

export default App;
