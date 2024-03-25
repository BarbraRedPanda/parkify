
const http = require('http');
const { Server } = require('socket.io');

// Create an HTTP server
const server = http.createServer();

// Create a Socket.IO server
// Create a Socket.IO server
const io = new Server(server, {
    cors: {
      origin: '*'
    }
  });
  

let captureRunning = true;

// Handle Socket.IO connections
io.on('connection', (socket) => {
    console.log('Socket.IO connected');

    // Handle incoming messages from clients
    io.on('toggleCapture', () => {
        console.log('hello world');
        toggleCapture();
    });

    io.on('apiResponse', (apiResponse) => {
        console.log('Python info receved!');
        // Passes json and image through to front end
        let json = JSON.parse(apiResponse[0]); 
        let streamData = apiResponse[1];
        const latitude = apiResponse[2];
        const longitude = apiResponse[3];

        const results = json.results;
        results.forEach( (result) => {
            const plate = {
                plateText: result.plate,
                score: result.score,
                region: result.region.code,
                type: result.vehicle.type,
                lat: latitude,
                lon: longitude,
                status: null,
                image: streamData
            };
            io.emit('plateRead', plate);
        });
    });
});


// Function to toggle image capture
function toggleCapture() {
    captureRunning = !captureRunning;
    console.log('Image capture loop toggled:', captureRunning ? 'ON' : 'OFF');
    // Send a message to the Raspberry Pi to toggle image capture
    io.emit(captureRunning ? 'captureOn' : "captureOff")
}

// Start the HTTP server
const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
