/**
 * Lightweight Local Development Server for SIH26034 P4 Frontend
 * Serves static assets and ES modules with correct MIME types and CORS headers.
 */

import http from "http";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 3000;

const MIME_TYPES = {
  ".html": "text/html",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".ts": "text/plain",
  ".css": "text/css",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
};

const server = http.createServer((req, res) => {
  // Normalize URL
  let reqPath = req.url.split("?")[0];
  if (reqPath === "/") reqPath = "/index.html";

  const safePath = path.normalize(path.join(__dirname, reqPath));
  if (!safePath.startsWith(__dirname)) {
    res.writeHead(403, { "Content-Type": "text/plain" });
    return res.end("403 Forbidden");
  }

  if (!fs.existsSync(safePath) || fs.statSync(safePath).isDirectory()) {
    // SPA fallback: return index.html for unknown HTML paths
    const indexPath = path.join(__dirname, "index.html");
    res.writeHead(200, { "Content-Type": "text/html", "Access-Control-Allow-Origin": "*" });
    return fs.createReadStream(indexPath).pipe(res);
  }

  const ext = path.extname(safePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || "application/octet-stream";

  res.writeHead(200, {
    "Content-Type": contentType,
    "Access-Control-Allow-Origin": "*",
    "Cache-Control": "no-cache",
  });
  fs.createReadStream(safePath).pipe(res);
});

server.listen(PORT, () => {
  console.log(`\n======================================================`);
  console.log(`SIH26034 Legal Metrology Compliance Frontend Server`);
  console.log(`Local URL: http://localhost:${PORT}`);
  console.log(`Tests URL: http://localhost:${PORT}/tests/index.html`);
  console.log(`======================================================\n`);
});
