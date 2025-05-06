const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const server = http.createServer(app);
const wss = new WebSocket.Server({
  server,
  clientTracking: true,
  perMessageDeflate: false,
});

wss.on('connection', (ws) => {
  console.log('A client connected:', ws._socket.remoteAddress);

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message.toString());
      console.log('Received data:', data);

      if (data.type === 'data' && data['send-data']) {
        // Broadcast to all connected clients
        wss.clients.forEach((client) => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(
              JSON.stringify({ type: 'data', 'send-data': data['send-data'] })
            );
          }
        });
      }
    } catch (error) {
      console.error('Error processing message:', error);
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected:', ws._socket.remoteAddress);
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

// Serve a basic endpoint for health check
app.get('/', (req, res) => {
  res.send('WebSocket server is running');
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

// Installation instructions:
// 1. Create a new directory and save this as server.js
// 2. Initialize npm: `npm init -y`
// 3. Install dependencies: `npm install express ws`
// 4. Run server: `node server.js`
