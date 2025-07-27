"use client"

import { useEffect, useState } from "react"

const API_URL = import.meta.env.VITE_API_URL

function App() {
  const [txns, setTxns] = useState([])
  const [error, setError] = useState(null)
  const [copiedId, setCopiedId] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 15

  // Nuevos estados:
  const [simCount, setSimCount] = useState(10)
  const [simInterval, setSimInterval] = useState(500)
  const [loadingSim, setLoadingSim] = useState(false)
  const [loadingClear, setLoadingClear] = useState(false)
  const [showControls, setShowControls] = useState(false)

  const fetchTxns = async () => {
    try {
      const res = await fetch(`${API_URL}/transactions`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setTxns(data)
      setError(null)
      const totalPages = Math.ceil(data.length / itemsPerPage)
      if (currentPage > totalPages && totalPages > 0) {
        setCurrentPage(totalPages)
      }
    } catch (e) {
      console.error(e)
      setError("Error al obtener transacciones")
    }
  }

  useEffect(() => {
    fetchTxns()
    const iv = setInterval(fetchTxns, 3000)
    return () => clearInterval(iv)
  }, [])

  const copyToClipboard = async (id) => {
    try {
      await navigator.clipboard.writeText(id)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (err) {
      console.error("Error al copiar:", err)
    }
  }

  // Paginación:
  const totalPages = Math.ceil(txns.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentTxns = txns.slice(startIndex, endIndex)

  const goToPage = (page) => {
    if (page < 1 || page > totalPages) return
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  // Handlers:
  const handleSimulate = async () => {
    setLoadingSim(true)
    setError(null)
    try {
      const res = await fetch(`${API_URL}/simulate?count=${simCount}&interval_ms=${simInterval}`, { method: "POST" })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      setTimeout(fetchTxns, (simInterval * simCount) / 1000 + 200)
    } catch (e) {
      console.error(e)
      setError("Error al simular transacciones")
    } finally {
      setLoadingSim(false)
    }
  }

  const handleSimulateDirect = async () => {
    setLoadingSim(true)
    setError(null)
    try {
      const res = await fetch(`${API_URL}/simulate-direct?count=${simCount}`, { method: "POST" })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      fetchTxns()
    } catch (e) {
      console.error(e)
      setError("Error al simular-direct")
    } finally {
      setLoadingSim(false)
    }
  }

  const handleClear = async () => {
    if (!window.confirm("¿Borrar todas las transacciones?")) return
    setLoadingClear(true)
    setError(null)
    try {
      const res = await fetch(`${API_URL}/transactions`, { method: "DELETE" })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      setTxns([])
      setCurrentPage(1)
    } catch (e) {
      console.error(e)
      setError("Error al borrar transacciones")
    } finally {
      setLoadingClear(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Contenedor principal centrado */}
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6">
        {/* Header mejorado */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-slate-800 mb-2">💳 Transacciones IoT</h1>
            <p className="text-slate-600 text-sm sm:text-base">Sistema de pagos en tiempo real</p>
            <div className="text-sm text-slate-500 hidden sm:block">🔄 Actualización automática cada 3s</div>
          </div>
          

          {/* Botón para mostrar/ocultar controles - ARREGLADO */}
          <div className="flex items-center gap-3 mt-4 sm:mt-0">
            <button
              onClick={() => setShowControls(!showControls)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors shadow-sm"
            >
              <span>⚡ Controles</span>
              <span className={`transform transition-transform ${showControls ? "rotate-180" : ""}`}>↓</span>
            </button>
          </div>
        </div>

        {/* Panel de controles colapsible */}
        {showControls && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 mb-6 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-slate-200">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2">🎛️ Panel de Control</h3>
            </div>

            <div className="p-4">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Configuración - INPUTS ARREGLADOS */}
                <div className="space-y-4">
                  <h4 className="font-medium text-slate-700 flex items-center gap-2">⚙️ Configuración</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-slate-600 mb-1">Cantidad de transacciones</label>
                      <input
                        type="number"
                        min="1"
                        max="100"
                        value={simCount}
                        onChange={(e) => setSimCount(Number(e.target.value))}
                        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-600 mb-1">Intervalo (ms)</label>
                      <input
                        type="number"
                        min="0"
                        max="5000"
                        value={simInterval}
                        onChange={(e) => setSimInterval(Number(e.target.value))}
                        className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400"
                      />
                    </div>
                  </div>
                </div>

                {/* Simulación */}
                <div className="space-y-4">
                  <h4 className="font-medium text-slate-700 flex items-center gap-2">🚀 Simulación</h4>
                  <div className="space-y-3">
                    <button
                      onClick={handleSimulate}
                      disabled={loadingSim}
                      className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2.5 rounded-lg font-medium transition-colors shadow-sm flex items-center justify-center gap-2"
                    >
                      {loadingSim ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          Simulando...
                        </>
                      ) : (
                        <>📡 Simular MQTT ({simCount})</>
                      )}
                    </button>

                    <button
                      onClick={handleSimulateDirect}
                      disabled={loadingSim}
                      className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-4 py-2.5 rounded-lg font-medium transition-colors shadow-sm flex items-center justify-center gap-2"
                    >
                      {loadingSim ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          Simulando...
                        </>
                      ) : (
                        <>⚡ Simular Directo ({simCount})</>
                      )}
                    </button>
                  </div>
                </div>

                {/* Gestión */}
                <div className="space-y-4">
                  <h4 className="font-medium text-slate-700 flex items-center gap-2">🗑️ Gestión</h4>
                  <div className="space-y-3">
                    <button
                      onClick={handleClear}
                      disabled={loadingClear}
                      className="w-full bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white px-4 py-2.5 rounded-lg font-medium transition-colors shadow-sm flex items-center justify-center gap-2"
                    >
                      {loadingClear ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          Borrando...
                        </>
                      ) : (
                        <>🗑️ Borrar Todas</>
                      )}
                    </button>

                    <button
                      onClick={fetchTxns}
                      className="w-full bg-slate-600 hover:bg-slate-700 text-white px-4 py-2.5 rounded-lg font-medium transition-colors shadow-sm flex items-center justify-center gap-2"
                    >
                      🔄 Actualizar
                    </button>
                  </div>
                </div>
              </div>

              {error && (
                <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-red-700 text-sm font-medium flex items-center gap-2">⚠️ {error}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Estadísticas rápidas */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-600 text-sm">Total Transacciones</p>
                <p className="text-2xl font-bold text-slate-800">{txns.length}</p>
              </div>
              <div className="text-2xl">📊</div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-600 text-sm">Aprobadas</p>
                <p className="text-2xl font-bold text-green-600">
                  {txns.filter((t) => ["approved", "completed", "success"].includes(t.status)).length}
                </p>
              </div>
              <div className="text-2xl">✅</div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-600 text-sm">Rechazadas</p>
                <p className="text-2xl font-bold text-red-600">
                  {txns.filter((t) => ["rejected", "failed", "error"].includes(t.status)).length}
                </p>
              </div>
              <div className="text-2xl">❌</div>
            </div>
          </div>
        </div>

        {/* Tabla de transacciones */}
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
                  <th className="text-center py-4 px-6 font-semibold text-slate-700">ID Transacción</th>
                  <th className="text-center py-4 px-6 font-semibold text-slate-700">Monto</th>
                  <th className="text-center py-4 px-6 font-semibold text-slate-700">Estado</th>
                  <th className="text-center py-4 px-6 font-semibold text-slate-700">Fecha y Hora</th>
                </tr>
              </thead>
              <tbody>
                {currentTxns.map((tx, index) => (
                  <tr
                    key={tx.id}
                    className={`
                      hover:bg-slate-50 transition-colors duration-150
                      ${index % 2 === 0 ? "bg-white" : "bg-slate-25"}
                      border-b border-slate-100 last:border-b-0
                    `}
                  >
                    <td className="py-4 px-6 text-center">
                      <div className="relative inline-block">
                        <button
                          onClick={() => copyToClipboard(tx.id)}
                          className="bg-blue-50 hover:bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm font-mono transition-colors duration-150 cursor-pointer border border-blue-200 hover:border-blue-300 shadow-sm"
                          title="Clic para copiar ID completo"
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
                      <span className="font-semibold text-slate-800">${tx.amount}</span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span
                        className={`
                        inline-flex items-center px-3 py-1 rounded-full text-sm font-medium capitalize
                        ${
                          tx.status === "approved" || tx.status === "completed" || tx.status === "success"
                            ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                            : tx.status === "rejected" || tx.status === "failed" || tx.status === "error"
                              ? "bg-red-100 text-red-800 border border-red-200"
                              : tx.status === "pending"
                                ? "bg-amber-100 text-amber-800 border border-amber-200"
                                : "bg-slate-100 text-slate-700 border border-slate-200"
                        }
                      `}
                      >
                        {tx.status}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-center text-slate-600 text-sm">
                      {new Date(tx.timestamp).toLocaleString("es-ES", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                      })}
                    </td>
                  </tr>
                ))}

                {currentTxns.length === 0 && txns.length > 0 && (
                  <tr>
                    <td colSpan="4" className="py-12 text-center">
                      <div className="text-slate-400">
                        <div className="text-4xl mb-3">📄</div>
                        <p className="text-lg font-medium text-slate-500">No hay transacciones en esta página</p>
                        <button onClick={() => goToPage(1)} className="mt-2 text-blue-600 hover:text-blue-800 text-sm">
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
                        <p className="text-lg font-medium text-slate-500">No hay transacciones aún</p>
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

          {/* Controles de paginación - ARREGLADOS */}
          {totalPages > 1 && (
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-200">
              <div className="flex justify-center items-center space-x-2">
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    currentPage === 1
                      ? "text-slate-400 cursor-not-allowed"
                      : "text-slate-600 hover:text-white hover:bg-blue-600"
                  }`}
                >
                  ← Anterior
                </button>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                  const showPage =
                    page === 1 || page === totalPages || (page >= currentPage - 1 && page <= currentPage + 1)

                  if (!showPage) {
                    if (page === 2 && currentPage > 4) {
                      return (
                        <span key={page} className="text-slate-400">
                          ...
                        </span>
                      )
                    }
                    if (page === totalPages - 1 && currentPage < totalPages - 3) {
                      return (
                        <span key={page} className="text-slate-400">
                          ...
                        </span>
                      )
                    }
                    return null
                  }

                  return (
                    <button
                      key={page}
                      onClick={() => goToPage(page)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                        currentPage === page
                          ? "bg-blue-600 text-white"
                          : "text-slate-600 hover:text-white hover:bg-blue-600"
                      }`}
                    >
                      {page}
                    </button>
                  )
                })}

                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    currentPage === totalPages
                      ? "text-slate-400 cursor-not-allowed"
                      : "text-slate-600 hover:text-white hover:bg-blue-600"
                  }`}
                >
                  Siguiente →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
