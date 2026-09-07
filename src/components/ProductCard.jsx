export default function ProductCard(props) {
  const {
    nombre = props.producto?.nombre,
    precio_final = props.producto?.precio_final,
    cuotas_cantidad = props.producto?.cuotas_cantidad,
    cuotas_valor = props.producto?.cuotas_valor,
    garantia_meses = props.producto?.garantia_meses,
    stock = props.producto?.stock,
    imagen = props.producto?.imagen,
  } = props;

  return (
    <div className="bg-white rounded-2xl shadow-sm hover:shadow-md transition-all duration-200 border border-slate-200 p-5 flex flex-col justify-between">
      <div>
        <div className="h-44 bg-slate-50 rounded-xl mb-4 flex items-center justify-center border border-slate-100 overflow-hidden relative">
          {imagen ? (
            <img src={imagen} alt={nombre} className="h-full w-full object-cover" />
          ) : (
            <div className="text-slate-400 text-center p-4">
              <svg className="w-12 h-12 mx-auto mb-1 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              <span className="text-xs font-medium">Sin imagen</span>
            </div>
          )}
          {stock !== undefined && (
            <span className="absolute top-2 right-2 bg-slate-900/80 backdrop-blur-xs text-white text-[11px] font-medium px-2 py-0.5 rounded-full">
              Stock: {stock}
            </span>
          )}
        </div>

        <h3 className="font-semibold text-slate-800 text-lg mb-2 line-clamp-2 leading-snug">
          {nombre || 'Producto'}
        </h3>

        <div className="mb-3">
          <span className="text-2xl font-bold text-slate-900">
            ${precio_final !== undefined && precio_final !== null ? Number(precio_final).toLocaleString('es-AR') : '0'}
          </span>
        </div>

        {Boolean(cuotas_cantidad && cuotas_valor) && (
          <p className="text-sm font-medium text-emerald-600 mb-2">
            {cuotas_cantidad} cuotas de ${Number(cuotas_valor).toLocaleString('es-AR')}
          </p>
        )}

        {Boolean(garantia_meses) && (
          <p className="text-xs text-slate-500 mb-4">
            Garantía: {garantia_meses} {garantia_meses === 1 ? 'mes' : 'meses'}
          </p>
        )}
      </div>

      <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 rounded-xl transition-colors duration-200 cursor-pointer text-sm shadow-xs">
        Agregar al carrito
      </button>
    </div>
  );
}
