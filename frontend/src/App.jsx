import './App.css'

import { useEffect, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [txns, setTxns] = useState([]);
  const [error, setError] = useState(null);
  const [copiedId, setCopiedId] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;

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

  const copyToClipboard = async (id) => {
    try {
      await navigator.clipboard.writeText(id);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000); // Ocultar después de 2 segundos
    } catch (err) {
      console.error('Error al copiar:', err);
    }
  };

  // Cálculos de paginación
  const totalPages = Math.ceil(txns.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentTxns = txns.slice(startIndex, endIndex);

  const goToPage = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
          {/* Información de paginación */}
          {txns.length > 0 && (
            <div className="px-6 py-3 bg-slate-50 border-b border-slate-200 flex justify-between items-center text-sm text-slate-600">
              <span>
                Mostrando {startIndex + 1}-{Math.min(endIndex, txns.length)} de {txns.length} transacciones
              </span>
              <span>
                Página {currentPage} de {totalPages}
              </span>
            </div>
          )}
          
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
                {currentTxns.map((tx, index) => (
                  <tr 
                    key={tx.id} 
                    className={`
                      hover:bg-slate-50 transition-colors duration-150
                      ${index % 2 === 0 ? 'bg-white' : 'bg-slate-25'}
                      border-b border-slate-100 last:border-b-0
                    `}
                  >
                    <td className="py-4 px-6 text-center">
                      <div className="relative inline-block">
                        <button
                          onClick={() => copyToClipboard(tx.id)}
                          className="bg-gray-50 hover:bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm font-mono transition-colors duration-150 cursor-pointer border border-gray-200 hover:border-gray-300 shadow-sm"
                          title="Clic para copiar ID completo"
                          style={{
                            backgroundColor: '#f9fafb',
                            color: '#374151',
                            borderColor: '#e5e7eb'
                          }}
                        >
                          {tx.id.slice(0, 8)}...
                        </button>
                        {copiedId === tx.id && (
                          <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-green-600 text-white text-xs px-2 py-1 rounded shadow-lg">
                            ¡Copiado!
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="font-semibold text-slate-800">
                        ${tx.amount}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-center">
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
                    <td className="py-4 px-6 text-center text-slate-600 text-sm">
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
                
                
                {currentTxns.length === 0 && txns.length > 0 && (
                  <tr>
                    <td colSpan="4" className="py-12 text-center">
                      <div className="text-slate-400">
                        <div className="text-4xl mb-3">📄</div>
                        <p className="text-lg font-medium text-slate-500">
                          No hay transacciones en esta página
                        </p>
                        <button 
                          onClick={() => goToPage(1)}
                          className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Ir a la primera página
                        </button>
                      </div>
                    </td>
                  </tr>
                )}

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
          
          {/* Controles de paginación */}
          {totalPages > 1 && (
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-200">
              <div className="flex justify-center items-center space-x-2">
                {/* Botón Anterior */}
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    currentPage === 1
                      ? 'text-slate-400 cursor-not-allowed'
                      : 'text-slate-600 hover:text-slate-800 hover:bg-white'
                  }`}
                >
                  ← Anterior
                </button>

                {/* Números de página */}
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => {
                  // Mostrar siempre primera, última y páginas cercanas a la actual
                  const showPage = page === 1 || page === totalPages || 
                    (page >= currentPage - 1 && page <= currentPage + 1);
                  
                  if (!showPage) {
                    // Mostrar "..." si hay páginas omitidas
                    if (page === 2 && currentPage > 4) {
                      return <span key={page} className="text-slate-400">...</span>;
                    }
                    if (page === totalPages - 1 && currentPage < totalPages - 3) {
                      return <span key={page} className="text-slate-400">...</span>;
                    }
                    return null;
                  }

                  return (
                    <button
                      key={page}
                      onClick={() => goToPage(page)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                        currentPage === page
                          ? 'bg-blue-600 text-white'
                          : 'text-slate-600 hover:text-slate-800 hover:bg-white'
                      }`}
                    >
                      {page}
                    </button>
                  );
                })}

                {/* Botón Siguiente */}
                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    currentPage === totalPages
                      ? 'text-slate-400 cursor-not-allowed'
                      : 'text-slate-600 hover:text-slate-800 hover:bg-white'
                  }`}
                >
                  Siguiente →
                </button>
              </div>
            </div>
          )}
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