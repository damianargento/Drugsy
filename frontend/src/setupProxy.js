const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Configuración específica para cada ruta de API
  const apiProxy = createProxyMiddleware({
    target: 'http://localhost:9000',
    changeOrigin: true,
    logLevel: 'debug',
    onProxyReq: (proxyReq, req, res) => {
      // Log para depuración
      console.log(`Proxying ${req.method} ${req.url} to ${proxyReq.path}`);
    },
    onError: (err, req, res) => {
      console.error('Proxy error:', err);
      res.writeHead(500, {
        'Content-Type': 'text/plain'
      });
      res.end(`Proxy error: ${err.message}`);
    }
  });

  // Aplicar el proxy solo a rutas específicas
  ['/token', '/register', '/users', '/chat', '/welcome'].forEach(path => {
    app.use(path, apiProxy);
  });
};
