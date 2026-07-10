const http = require('http');
const { ParallaxAOS } = require('./aos');
const { listAcyilaInterfaces } = require('./acyila');
const { reconcileSnapshot } = require('./reconciliation');
const { walletStatement } = require('./statements');
const { dashboardContract } = require('./dashboard_contract');

const aos = new ParallaxAOS();
const host = process.env.PARALLAX_WALLET_HOST || '127.0.0.1';
const port = Number(process.env.PARALLAX_WALLET_PORT || 8799);

function json(res, status, body) {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body, null, 2));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 1024 * 1024) reject(new Error('request too large'));
    });
    req.on('end', () => resolve(body ? JSON.parse(body) : {}));
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'GET' && req.url === '/health') return json(res, 200, { ok: true, service: 'parallax-wallet-aos', version: '0.2.0' });
    if (req.method === 'GET' && req.url === '/interfaces') return json(res, 200, { interfaces: listAcyilaInterfaces() });
    if (req.method === 'GET' && req.url === '/dashboard-contract') return json(res, 200, dashboardContract());
    if (req.method === 'GET' && req.url === '/commands') return json(res, 200, { commands: aos.listCommands() });
    if (req.method === 'GET' && req.url === '/snapshot') return json(res, 200, aos.execute('system.snapshot'));
    if (req.method === 'POST' && req.url === '/reconcile') {
      const body = await readBody(req);
      return json(res, 200, reconcileSnapshot(aos.walletOS.snapshot(), body.externalBalances || {}));
    }
    if (req.method === 'POST' && req.url === '/statement') {
      const body = await readBody(req);
      return json(res, 200, walletStatement(aos.walletOS.snapshot(), body.walletId, body.options || {}));
    }
    if (req.method === 'POST' && req.url === '/execute') {
      const body = await readBody(req);
      return json(res, 200, aos.execute(body.command, body.input || {}));
    }
    return json(res, 404, { error: 'not_found' });
  } catch (error) {
    return json(res, 400, { error: error.message });
  }
});

if (require.main === module) {
  server.listen(port, host, () => console.log(`PARALLAX Wallet AOS listening on http://${host}:${port}`));
}

module.exports = { server, aos };
