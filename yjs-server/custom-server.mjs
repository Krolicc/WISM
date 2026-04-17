
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { setupWSConnection } from 'y-websocket/bin/utils';
import fetch from 'node-fetch';

const port = process.env.PORT || 1234;
const host = process.env.HOST || '0.0.0.0';
const server = createServer((_request, response) => {
    response.writeHead(200, { 'Content-Type': 'text/plain' });
    response.end('okay');
});

const wss = new WebSocketServer({ server });

const verifyConnection = async (info) => {
    const url = new URL(info.req.url, `http://${info.req.headers.host}`);
    const pathParts = url.pathname.split('/').filter(Boolean);
    const serviceName = pathParts[2];
    const token = url.searchParams.get('token');
    const room = url.pathname.split('/').pop();

    if (!token || !room) {
        console.warn('Connection attempt without token or room');
        return false;
    }

    let verifyUrl = '';
    if (serviceName === 'media') {
        verifyUrl = 'http://media:8002/api/v1/yjs/verify-connection';
    } else {
        verifyUrl = 'http://backend:8000/api/v1/yjs/verify-connection';
    }

    console.log(`Verifying connection for room: ${room}`);

    try {
        const response = await fetch(verifyUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ story_id: room, token: token })
        });

        if (response.ok) {
            console.log(`Connection verified for room: ${room}`);
            return true;
        } else {
            const errorText = await response.text();
            console.warn(`Connection denied for room: ${room}. Status: ${response.status}, Detail: ${errorText}`);
            return false;
        }
    } catch (error) {
        console.error(`Error verifying connection for room ${room}:`, error);
        return false;
    }
};

wss.on('connection', (conn, req) => {
    verifyConnection({ req }).then(isVerified => {
        if (isVerified) {
            const url = new URL(req.url, `http://${req.headers.host}`);
            const pathParts = url.pathname.split('/').filter(Boolean);
            const serviceName = pathParts[2]; 
            
            req.url = `/${serviceName}_${pathParts.pop()}`; 

            setupWSConnection(conn, req);
        } else {
            conn.close();
        }
    });
});

server.listen(port, host, () => {
    console.log(`y-websocket server running on '${host}' port '${port}'`);
});

