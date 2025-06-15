import './App.css'

import { useEffect, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [txns, setTxns] = useState([]);
  const [error, setError] = useState(null);

  const fetchTxns = async () => {
    try {
      const res = await fetch(`${API_URL}/transactions`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setTxns(data);
      setError(null);
    } catch (e) {
      console.error(e);
      setError("Error al obtener transacciones");
    }
  };

  useEffect(() => {
    fetchTxns();
    const iv = setInterval(fetchTxns, 3000);
    return () => clearInterval(iv);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-slate-800 mb-8">
          💳 Transacciones IoT Payments
        </h1>
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700 font-medium">⚠️ {error}</p>
          </div>
        )}
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-100 border-b border-slate-200">
                  <th className="text-center py-4 px-6 font-semibold text-slate-700">
                    ID Transacción
                  </th>
                  <th className="text-center py-4 px-6 font-semibold text-slate-700">
                    Monto
                  </th>
                  <th className="text-center py-4 px-6 font-semibold text-slate-700">
                    Estado
                  </th>
                  <th className="text-center py-4 px-6 font-semibold text-slate-700">
                    Fecha y Hora
                  </th>
                </tr>
              </thead>
              <tbody>
                {txns.map((tx, index) => (
                  <tr 
                    key={tx.id} 
                    className={`
                      hover:bg-slate-50 transition-colors duration-150
                      ${index % 2 === 0 ? 'bg-white' : 'bg-slate-25'}
                      border-b border-slate-100 last:border-b-0
                    `}
                  >
                    <td className="py-4 px-6">
                      <code className="bg-slate-100 text-slate-700 px-2 py-1 rounded text-sm font-mono">
                        {tx.id.slice(0, 8)}...
                      </code>
                    </td>
                    <td className="py-4 px-6">
                      <span className="font-semibold text-slate-800">
                        ${tx.amount}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <span className={`
                        inline-flex items-center px-3 py-1 rounded-full text-sm font-medium capitalize
                        ${tx.status === 'approved' || tx.status === 'completed' || tx.status === 'success' 
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' 
                          : tx.status === 'rejected' || tx.status === 'failed' || tx.status === 'error'
                          ? 'bg-red-100 text-red-800 border border-red-200'
                          : tx.status === 'pending' 
                          ? 'bg-amber-100 text-amber-800 border border-amber-200'
                          : 'bg-slate-100 text-slate-700 border border-slate-200'
                        }
                      `}>
                        {tx.status}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-slate-600 text-sm">
                      {new Date(tx.timestamp).toLocaleString('es-ES', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                      })}
                    </td>
                  </tr>
                ))}
                
                {txns.length === 0 && (
                  <tr>
                    <td colSpan="4" className="py-12 text-center">
                      <div className="text-slate-400">
                        <div className="text-4xl mb-3">📊</div>
                        <p className="text-lg font-medium text-slate-500">
                          No hay transacciones aún
                        </p>
                        <p className="text-sm text-slate-400 mt-1">
                          Las transacciones aparecerán aquí cuando se procesen
                        </p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
        
        <div className="mt-6 text-center">
          <p className="text-slate-500 text-sm">
            🔄 Los datos se actualizan automáticamente cada 3 segundos
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;