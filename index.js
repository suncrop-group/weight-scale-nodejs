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

// Store client connections with their identifiers
const clients = new Map();

wss.on('connection', (ws) => {
  console.log('A client connected:', ws._socket.remoteAddress);

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message.toString());

      if (data.type === 'register') {
        // Register the client with its identifier
        const identifier = data.identifier;
        clients.set(identifier, ws);
        console.log(`Client registered with identifier: ${identifier}`);
        ws.send(
          JSON.stringify({
            type: 'registered',
            message: 'Successfully registered',
          })
        );
      } else if (data.type === 'data' && data.identifier && data['send-data']) {
        // Route data to the specific receiver
        const targetIdentifier = data.identifier;
        const targetClient = clients.get(targetIdentifier);

        if (targetClient && targetClient.readyState === WebSocket.OPEN) {
          targetClient.send(
            JSON.stringify({ type: 'data', 'send-data': data['send-data'] })
          );
          console.log(`Data sent to ${targetIdentifier}: ${data['send-data']}`);
        } else {
          console.log(`No client found for identifier: ${targetIdentifier}`);
          ws.send(
            JSON.stringify({ type: 'error', message: 'No receiver found' })
          );
        }
      }
    } catch (error) {
      console.error('Error processing message:', error);
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({ type: 'error', message: 'Invalid message format' })
        );
      }
    }
  });

  ws.on('close', (code, reason) => {
    console.log(`Disconnected. Code: ${code}, Reason: ${reason}`);
    // Clean up disconnected client from the map
    for (const [identifier, client] of clients) {
      if (client === ws) {
        clients.delete(identifier);
        console.log(`Removed client with identifier: ${identifier}`);
        break;
      }
    }
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

// Serve a basic endpoint for health check
app.get('/', (req, res) => {
  res.send('WebSocket server is running');
});

const PORT = process.env.PORT || 4000; // Updated to match your current port
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
