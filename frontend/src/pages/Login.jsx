import React, { useState } from 'react';
import axios from 'axios';

const Login = ({ setToken }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // FastAPI-க்கு லாகின் டேட்டாவை அனுப்புதல்
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post('http://localhost:8000/login', formData);
      
      // டோக்கனை லோக்கல் ஸ்டோரேஜில் சேமித்தல்
      localStorage.setItem('token', response.data.access_token);
      setToken(response.data.access_token);
    } catch (err) {
      setError('மின்னஞ்சல் அல்லது கடவுச்சொல் தவறானது!');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <form onSubmit={handleLogin} className="bg-slate-800 p-8 rounded-xl shadow-2xl w-96 border border-slate-700">
        <h2 className="text-3xl font-bold text-white mb-6 text-center text-purple-400">FraudShield Login</h2>
        {error && <p className="text-red-400 text-sm mb-4 text-center">{error}</p>}
        <input 
          type="email" placeholder="Email" 
          className="w-full p-3 mb-4 rounded bg-slate-700 text-white outline-none focus:ring-2 focus:ring-purple-500"
          onChange={(e) => setEmail(e.target.value)} required
        />
        <input 
          type="password" placeholder="Password" 
          className="w-full p-3 mb-6 rounded bg-slate-700 text-white outline-none focus:ring-2 focus:ring-purple-500"
          onChange={(e) => setPassword(e.target.value)} required
        />
        <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded transition-all">
          Login
        </button>
      </form>
    </div>
  );
};

export default Login;