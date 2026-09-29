const BASE_URL = import.meta.env?.VITE_API_URL || 'http://127.0.0.1:8000';

export const INITIAL_PRODUCTOS = [
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

// Alias export for backward compatibility
export const productos = INITIAL_PRODUCTOS;

function getAuthHeaders() {
  const token = localStorage.getItem('token') || localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function getProductos(params = {}) {
  try {
    let url = `${BASE_URL}/productos/`;
    if (params && typeof params === 'object' && Object.keys(params).length > 0) {
      const searchParams = new URLSearchParams(params);
      url = `${BASE_URL}/productos/?${searchParams.toString()}`;
    }

    let response = await fetch(url);
    if (!response.ok && url !== `${BASE_URL}/productos`) {
      response = await fetch('/api/productos');
    }

    if (response.ok) {
      return await response.json();
    }
    throw new Error(`HTTP error status ${response.status}`);
  } catch (error) {
    console.warn('Conexión con el servidor backend falló, usando INITIAL_PRODUCTOS como fallback:', error);
    return INITIAL_PRODUCTOS;
  }
}

export async function loginUser(credentials) {
  const payload = {
    email: credentials?.email || credentials?.username || '',
    username: credentials?.username || credentials?.email || '',
    password: credentials?.password || '',
  };

  const response = await fetch(`${BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error al iniciar sesión');
  }

  const data = await response.json();
  if (data.access_token) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('access_token', data.access_token);
  }
  return data;
}

export async function registerUser(userData) {
  const response = await fetch(`${BASE_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error en el registro');
  }

  return await response.json();
}

export async function getPerfil() {
  const response = await fetch(`${BASE_URL}/perfil`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error al obtener perfil');
  }

  return await response.json();
}

export async function getMisDatos() {
  const response = await fetch(`${BASE_URL}/usuarios/me`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error al obtener mis datos');
  }

  return await response.json();
}

export async function actualizarPerfil(data) {
  const response = await fetch(`${BASE_URL}/perfil`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error al actualizar perfil');
  }

  return await response.json();
}

export async function exportarMisDatos() {
  const response = await fetch(`${BASE_URL}/usuarios/exportar`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error al exportar mis datos');
  }

  return await response.blob();
}

export async function eliminarCuenta() {
  const response = await fetch(`${BASE_URL}/usuarios/me`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error al eliminar cuenta');
  }

  localStorage.removeItem('token');
  localStorage.removeItem('access_token');
  return true;
}

export async function crearPedido(pedidoData) {
  const response = await fetch(`${BASE_URL}/pedidos/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(pedidoData),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error al crear pedido');
  }

  return await response.json();
}

export async function getMisPedidos() {
  const response = await fetch(`${BASE_URL}/pedidos/`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error al obtener mis pedidos');
  }

  return await response.json();
}

export async function revocarPedido(id) {
  const response = await fetch(`${BASE_URL}/pedidos/${id}/revocar`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Error al revocar pedido');
  }

  return await response.json();
}
