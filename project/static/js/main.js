const currentUrl = window.location.href;
if (currentUrl.includes('compra')) {
  const scriptElement = document.createElement('script');
  scriptElement.src = '../static/js/compras.js';
  document.body.appendChild(scriptElement);

} else if (currentUrl.includes('inventario')){
  const scriptElement = document.createElement('script');
  scriptElement.src = '../static/js/inventario.js';
  document.body.appendChild(scriptElement);

} else if(currentUrl.includes('editarProducto')){
  const scriptElement = document.createElement('script');
  scriptElement.src = '../static/js/productos.js';
  document.body.appendChild(scriptElement);
  console.log(currentUrl)
}