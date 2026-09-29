import { useState, useEffect } from 'react';
import { getProductos } from '../services/api';
import ProductCard from './ProductCard';

export default function Catalog() {
  const [productos, setProductos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    setCargando(true);
    
    getProductos()
      .then((data) => {
        if (!isMounted) return;
        let items = [];
        if (Array.isArray(data)) {
          items = data;
        } else if (Array.isArray(data?.items)) {
          items = data.items;
        } else if (Array.isArray(data?.productos)) {
          items = data.productos;
        } else if (Array.isArray(data?.results)) {
          items = data.results;
        } else if (Array.isArray(data?.data)) {
          items = data.data;
        }
        setProductos(items);
      })
      .catch((err) => {
        if (!isMounted) return;
        console.error('Error al obtener productos:', err);
        setError('Ocurrió un error al cargar los productos');
      })
      .finally(() => {
        if (isMounted) {
          setCargando(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (cargando) {
    return (
      <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 shadow-xs">
        <p className="text-slate-500 font-medium animate-pulse">Cargando productos del catálogo...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 bg-white rounded-2xl border border-red-200 shadow-xs">
        <p className="text-red-500 font-medium">{error}</p>
      </div>
    );
  }

  return (
    <div>
      {productos.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 shadow-xs">
          <p className="text-slate-500 font-medium">No hay productos para mostrar.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {productos.map((producto, index) => (
            <ProductCard key={producto?.id || index} producto={producto} />
          ))}
        </div>
      )}
    </div>
  );
}
