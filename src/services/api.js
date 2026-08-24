// Productos definidos en el backend FastAPI (app/main.py)
export const productos = [
  {
    id: 1,
    nombre: "Cafetera Expreso Automática",
    precio_final: 320000.0,
    cuotas_cantidad: 6,
    cuotas_valor: 53333.33,
    garantia_meses: 12,
    stock: 20,
  },
  {
    id: 2,
    nombre: "Silla Gamer Ergonómica Pro",
    precio_final: 250000.0,
    cuotas_cantidad: 3,
    cuotas_valor: 83333.33,
    garantia_meses: 6,
    stock: 12,
  },
  {
    id: 3,
    nombre: 'Monitor Gamer 27" 165Hz IPS',
    precio_final: 410000.0,
    cuotas_cantidad: 12,
    cuotas_valor: 34166.67,
    garantia_meses: 24,
    stock: 8,
  },
  {
    id: 4,
    nombre: "Teclado Mecánico RGB Switch Red",
    precio_final: 85000.0,
    cuotas_cantidad: 3,
    cuotas_valor: 28333.33,
    garantia_meses: 12,
    stock: 30,
  },
  {
    id: 5,
    nombre: "Consola de Videojuegos 1TB",
    precio_final: 890000.0,
    cuotas_cantidad: 12,
    cuotas_valor: 74166.67,
    garantia_meses: 12,
    stock: 5,
  },
];

export async function getProductos() {
  try {
    // 1. Intentar mediante el proxy configurado en Vite (/api/productos)
    const response = await fetch('/api/productos');
    if (response.ok) {
      return await response.json();
    }

    // 2. Intentar conexión directa a la URL de FastAPI
    const directResponse = await fetch('http://127.0.0.1:8000/productos');
    if (directResponse.ok) {
      return await directResponse.json();
    }

    throw new Error('Respuesta no válida del servidor');
  } catch (error) {
    console.warn('Conexión con el servidor backend en curso/fallback a datos de api.js:', error);
    return productos;
  }
}
