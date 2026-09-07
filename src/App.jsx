import { useState, useEffect } from 'react';
import { getProductos } from './services/api';
import ProductCard from './components/ProductCard';

function App() {
  const [productos, setProductos] = useState([]);

  useEffect(() => {
    getProductos()
      .then((data) => {
        setProductos(data);
      })
      .catch((error) => {
        console.error('Error al cargar los productos:', error);
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-blue-600 flex items-center gap-2">
            🛍️ Tiendita
          </h1>
          <span className="text-sm font-medium text-slate-500">
            {productos.length} {productos.length === 1 ? 'producto' : 'productos'}
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Catálogo de Productos</h2>
        
        {productos.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <p className="text-slate-500 font-medium">No hay productos para mostrar.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {productos.map((producto, index) => (
              <ProductCard
                key={producto.id || index}
                {...producto}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;