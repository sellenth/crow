const express = require('express')
const app = express()
const http = require('http')
const path = require('path')
const cors = require('cors')
const socketIO = require('socket.io')
const fs = require('fs')
const net = require('net');
const client = new net.Socket();
const cookieParser = require('cookie-parser')
const port = 3001
const pathToSettings = '../shamir/code/settings.py';
var settings = {}

// Middleware
app.use(express.static('public'))
// Serve the static files from the React app
app.use(express.static(path.join(__dirname, './../ui/build')));
app.use(express.json())
app.use(cookieParser())
app.use(cors())


// Authentication route
app.post('/auth', (req, res) => {
  const username = req.body.username;
  const pw = req.body.pw;

  if (pw === '111' || pw === '222'){

    client.connect(55556, 'localhost', function () {
      //client.write(username + ':' + pw); THE ACTUAL MESSAGE TO SEND
      pw === '111' ? 
        client.write("r3k has submitted 1 shares!") // demo message
        : client.write("tim has submitted 1 shares!") // demo message
    })

    client.on('error', function(err){
      console.log("Error: "+err.message);
    })

    client.close
  }

  res.status(200).send()
})

app.get('/keypad', (req, res) => {
  res.sendFile(path.join(__dirname + '/public/html/index.html'));
})


// Send settings.py as json
app.get('/settings', (req, res) => {
  res.json(settings);
})

// Serve correct homescreen for node type
app.get('/sendit', (req, res) => {
  //caw();
  io.sockets.emit('testchannel',
    "Sending Update to Client Node\n" +
    "Got share\n" +
    "Node registered: web\n" +
    "Node registered: face\n" +
    "Node registered: web\n" +
    "Sending New Share to other Auth Nodes\n" + 
    "Sending Update to Client Node\n" +
    "Got share\n" +
    "Sending New Share to other Auth Nodes\n" + 
    "Recieved Share from Client Node\n" +
    "r3k has submitted 1 shares!\n" +
    "tim has submitted 1 shares!\n" +
    "r3k has submitted 1 shares!\n" +
    "r3k has submitted 1 shares!\n" +
    "r3k has submitted 1 shares!\n" +
    "(r3k) is Authorized!\n"
    )
  res.send('hi')
})

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + './../ui/build/index.html'));
})

function caw(){
  var spawn = require('child_process').spawn;
  var process = spawn('netcat', 
    ["-l", "-p", "55556", "-k"],
    {cwd: '../shamir/code/'})

  process.stdout.on('data', function(data){
    console.log(data.toString())
    io.sockets.emit('testchannel', data.toString())
  })

  process.stderr.on('data', function(data){
    console.log(data.toString())
  });
}

function parseSettings(settingsFile){
  let line = null;

  for (let l = 0; l < settingsFile.length; l++){
    line = settingsFile[l];
    if (line.includes("ID")) {
      settings["id"] = line.substring(
        line.indexOf("'") + 1,
        line.lastIndexOf("'"))
    }

    else if (line.includes("THRESH")) {
      settings["threshold"] = line.substring(
        line.lastIndexOf(" ") + 1,
        line.length)
    }

    else if (line.includes("TOTAL")) {
      settings["total"] = line.substring(
        line.lastIndexOf(" ") + 1,
        line.length)
    }
  }
  return settings;
}

fs.watchFile(pathToSettings, (curr, prev) => {
  console.log('Settings file has changed');
  readSettingsFile();
  try {
    io.sockets.emit("SettingsUpdate", "pass") 
  } catch (err) {
    console.log('SOCKET ERROR: ' + err)
  }
});

function readSettingsFile() {
  try {
    let settingsFile = fs.readFileSync(pathToSettings, 'utf8').split('\n');
    parseSettings(settingsFile)
  } catch (err){
    console.log(err)
    console.log("\n\nFailed to read node settings, aborting");
    process.exit(1)
  }
}

var os = require( 'os' );
var networkInterfaces = Object.values(os.networkInterfaces())
    .reduce((r,a)=>{
        r = r.concat(a)
        return r;
    }, [])
    .filter(({family, address}) => {
        return family.toLowerCase().indexOf('v4') >= 0 &&
            address !== '127.0.0.1'
    })
    .map(({address}) => address);
var ipAddresses = networkInterfaces.join(', ')

const server = http.createServer(app)
    .listen(port, () => {
        readSettingsFile();
        caw();
        console.log('Connect to server at ' + ipAddresses + ':' + port)
    })

const io = socketIO(server);

io.on("connection", socket => {
  socket.on("disconnect", () => console.log('A client disconnected'));
})
