const express = require('express')
const app = express()
const http = require('http')
const path = require('path')
const cors = require('cors')
const sha256 = require('js-sha256').sha256
const socketIO = require('socket.io')
const spawn = require('child_process').spawn;
const fs = require('fs')
const net = require('net');
const client = new net.Socket();
const cookieParser = require('cookie-parser')
const port = 3001
const pathToSettings = '../shamir/code/settings.py';
const settings = {}

// Middleware
app.use(express.static('public'))
// Serve the static files from the React app
app.use(express.static(path.join(__dirname, './../ui/build')));
app.use(express.json())
app.use(cookieParser())
app.use(cors())


// Authentication route
app.post('/auth', (req, res) => {
  console.log('-- In Authentication route')
  const username = req.body.username;
  const pw = req.body.pw;
  CommWithSocket(username, pw)
  res.status(200).send()
})

function CommWithSocket(username, password){
    let pw_hash = sha256(password)
    let buff = new Buffer(pw_hash)
    let base64enc = buff.toString('base64')
    let payload = username + ':'+ base64enc
    console.log("-- In CommWithSocket, received this payload: " + payload)
    console.log("-- The username is: " + username + ' and the password is: ' + password)
    client.connect(55556, 'localhost', function () {
      client.write(payload)
    })

    client.on('error', function(err){
      console.error(err);
      client.destroy()
    })

    // getting errors that socket was already connected
    // now destroying socket after .25 seconds
    // might become problematic if message can't be sent
    // that quickly
    client.setTimeout(250, () => {
      client.destroy()
    })

    client.close

}

app.get('/keypad', (req, res) => {
  res.sendFile(path.join(__dirname + '/public/html/index.html'));
})


// Send settings.py as json
app.get('/settings', (req, res) => {
  res.json(settings);
})

// an endpoint for testing, will remove
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
    "jim has submitted 1 shares!\n" +
    "prim has submitted 1 shares!\n" +
    "r3k has submitted 1 shares!\n" +
    "r3k has submitted 1 shares!\n" +
    "r3k has submitted 1 shares!\n" +
    "(r3k) is Authorized!\n"
    )
  res.end()
})

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + './../ui/build/index.html'));
})

function caw(){
  console.log('-- Spawning crow caw process')
  var process = spawn('crow_caw', [],
    {cwd: '../shamir/code/'})

  process.stdout.on('data', function(data){
    console.log('-- Caw stdout: ' + data.toString())
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
  socket.on("qrchannel", (username, password) => CommWithSocket(username, password));
  socket.on("voiceChannel", (username, dat) => VoiceRecognition(username, dat));
})

function VoiceRecognition(username, blob) {
  fs.writeFile('../voice-recognition/capture.ogg', blob, (err) => {
    if (!err) {

      var process = spawn('ffmpeg',
        ["-i", "./capture.ogg", "-vn", "./capture.wav", "-y"],
        { cwd: '../voice-recognition/' })

      process.on('close', () => {
        var p2 = spawn('python3',
          ["voice.py", "halston", "capture.wav"],
          { cwd: '../voice-recognition/' })
        
          p2.stdout.on('data', function (data) {
            console.log('-- In voice recognition, transcript is: ' + data.toString())
            let payload = username + ':' + data.toString()
            //CommWithSocket(payload)
            io.sockets.emit('voiceChannel', data.toString())
          })

          process.stderr.on('data', function (data) {
            console.error(data.toString())
          });
      })
    }
  })
}