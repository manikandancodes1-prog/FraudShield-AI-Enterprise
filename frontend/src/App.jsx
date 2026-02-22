import React, { useEffect, useState } from 'react';
import { Activity, ShieldAlert, CheckCircle, AlertTriangle, Zap, Download, LogOut } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

// Toastify & Excel Imports
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import * as XLSX from 'xlsx';


import Login from './pages/Login'; 


function Dashboard({ onLogout }) {
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState({ total: 0, highRisk: 0, approved: 0 });

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/transactions');
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.status === "Blocked" || data.status === "Flagged") {
        toast.error(`🚨 FRAUD ALERT: Transaction Blocked! \nID: ${data.transaction_id.split('-')[0]}`, {
          position: "top-right",
          autoClose: 5000,
          theme: "dark",
        });
      }

      setTransactions(prev => [data, ...prev].slice(0, 15)); 
      setStats(prev => ({
        total: prev.total + 1,
        highRisk: data.risk_score > 70 ? prev.highRisk + 1 : prev.highRisk,
        approved: data.status === 'Approved' ? prev.approved + 1 : prev.approved
      }));
    };

    socket.onerror = (error) => console.error("WebSocket Connection Error:", error);
    return () => socket.close();
  }, []);

  const exportToExcel = () => {
    if (transactions.length === 0) {
      toast.warn("ஏற்றுமதி செய்ய தரவுகள் இல்லை!");
      return;
    }
    const worksheet = XLSX.utils.json_to_sheet(transactions);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Fraud_Report");
    XLSX.writeFile(workbook, `FraudShield_Report_${new Date().toLocaleTimeString()}.xlsx`);
    toast.success("Excel report downloaded successfully! ✅");
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-slate-200 p-8 font-sans">
      <ToastContainer position="top-right" />
      
      {/* Header Section */}
      <div className="max-w-7xl mx-auto flex justify-between items-center mb-10">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            FraudShield AI
          </h1>
          <p className="text-slate-500 text-sm mt-1 flex items-center gap-2">
            <Zap size={14} className="text-yellow-500" /> Advanced Real-time Monitoring
          </p>
        </div>
        <div className="flex gap-4 items-center">
          <div className="bg-[#141417] border border-slate-800 px-5 py-2 rounded-full text-xs font-mono shadow-lg shadow-indigo-500/10">
            SYSTEM STATUS: <span className="text-green-500 animate-pulse">● ONLINE</span>
          </div>
          {/* Logout Button */}
          <button 
            onClick={onLogout}
            className="flex items-center gap-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-bold py-2 px-4 rounded-xl border border-red-500/20 transition-all"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <StatCard title="Total Scanned" value={stats.total} icon={<Activity size={24} />} color="indigo" />
          <StatCard title="High Risk Alerts" value={stats.highRisk} icon={<AlertTriangle size={24} />} color="red" />
          <StatCard title="Safe Transactions" value={stats.approved} icon={<CheckCircle size={24} />} color="emerald" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-[#141417] border border-slate-800 rounded-3xl p-8 shadow-2xl">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold flex items-center gap-3">
                <ShieldAlert className="text-indigo-400" /> Live Intelligence Feed
              </h2>
              <button 
                onClick={exportToExcel}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-2.5 px-5 rounded-xl transition-all shadow-lg shadow-indigo-500/20 active:scale-95"
              >
                <Download size={16} /> Export Report
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-slate-500 text-xs uppercase tracking-widest border-b border-slate-800/50">
                    <th className="pb-5 font-semibold">ID</th>
                    <th className="pb-5 font-semibold">Amount</th>
                    <th className="pb-5 font-semibold">Risk Analysis</th>
                    <th className="pb-5 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  <AnimatePresence initial={false}>
                    {transactions.map((tx) => (
                      <motion.tr 
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        key={tx.transaction_id} 
                        className="border-b border-slate-800/30 hover:bg-slate-800/20"
                      >
                        <td className="py-5 font-mono text-slate-400 text-xs">{tx.transaction_id.split('-')[0]}...</td>
                        <td className="py-5 font-bold text-lg">${tx.amount}</td>
                        <td className="py-5 font-mono text-xs text-indigo-400">{tx.risk_score}% Risk</td>
                        <td className="py-5 font-bold text-xs">{tx.status}</td>
                      </motion.tr>
                    ))}
                  </AnimatePresence>
                </tbody>
              </table>
            </div>
          </div>
          {/* Chart Section - ஏற்கனவே உள்ளதை அப்படியே வைக்கவும் */}
        </div>
      </div>
    </div>
  );
}

// --- 🛡️ Main App Logic (The Gatekeeper) ---
function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  
  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    toast.info("Logged out successfully");
  };

  
  if (!token) {
    return <Login setToken={setToken} />;
  }

  
  return <Dashboard onLogout={handleLogout} />;
}


function StatCard({ title, value, icon, color }) {
  const themes = {
    indigo: { border: 'group-hover:border-indigo-500/50', iconBg: 'text-indigo-500 bg-indigo-500/10', gradient: 'from-indigo-500/10 to-transparent' },
    red: { border: 'group-hover:border-red-500/50', iconBg: 'text-red-500 bg-red-500/10', gradient: 'from-red-500/10 to-transparent' },
    emerald: { border: 'group-hover:border-emerald-500/50', iconBg: 'text-emerald-500 bg-emerald-500/10', gradient: 'from-emerald-500/10 to-transparent' }
  };
  const theme = themes[color];
  return (
    <div className={`bg-[#141417] border border-slate-800 p-8 rounded-3xl relative overflow-hidden group hover:scale-[1.02] transition-all duration-300 ${theme.border}`}>
      <div className="flex justify-between items-start z-10 relative">
        <div>
          <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">{title}</p>
          <h3 className="text-4xl font-black mt-2 tracking-tight text-white">{value}</h3>
        </div>
        <div className={`p-4 rounded-2xl ${theme.iconBg}`}>{icon}</div>
      </div>
    </div>
  );
}

export default App;