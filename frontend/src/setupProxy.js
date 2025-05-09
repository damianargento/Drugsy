const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Configuración para interceptar todas las solicitudes al backend
  app.use(
    createProxyMiddleware({
      target: 'http://localhost:9000',
      changeOrigin: true,
      // Sin pathRewrite ya que queremos mantener las rutas originales
      logLevel: 'debug',
      // Solo interceptar solicitudes que no sean para archivos estáticos o del frontend
      context: [
        '/token', '/register', '/users', '/chat', '/welcome',
        // Agrega aquí más rutas del backend según sea necesario
      ]
    })
  );
};
