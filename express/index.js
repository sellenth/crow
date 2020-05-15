const express = require('express')
const app     = express()
const https    = require('https')
const path    = require('path')
const cors    = require('cors')
const sha256  = require('js-sha256').sha256
const fs      = require('fs')
const net     = require('net');
const spawn   = require('child_process').spawn;
const client  = new net.Socket();
const port    = process.env.PORT || 3001
const devOut  = require('debug')('dev')
const socketIO = require('socket.io')
const settings = {}
const cookieParser   = require('cookie-parser')
const pathToSettings = '../shamir/code/settings.py';

const options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
};

// Middleware
app.use(express.static(path.join(__dirname, './../ui/build')));
app.use(express.json())
app.use(cookieParser())
app.use(cors())


// Authentication route
app.post('/auth', (req, res) => {
  console.log('-- In Authentication route')
  const username = req.body.username;
  const pw = req.body.pw;
  const register = req.body.register;
  CommWithSocket(username, pw, register)
  res.status(200).send()
})




// This function sends user data to 55556 where it is
// ingested by crow_caw and processed by the client/auth node
function CommWithSocket(username, password, registerFlag){
    if (password.length > 66){
      io.emit("ErrChannel", "Password is too long to be securely hashed, try a shorter one")
      return
    }
    devOut("-- The username is: " + username + ' and the password is: ' + password)
    let payload

    // When registering a user we send only a hash of their password
    if (registerFlag) {
      devOut("-- User is being registered")
      let pw_hash = sha256(password)
      devOut("-- Length of pw hash is: " + pw_hash.length)
      let buff = new Buffer(pw_hash)
      password = buff.toString('base64')
      payload = password
    }
    // When authenticating a user, we send their username and password (unhashed)
    else {
      payload = username + ':' + password
    }

    console.log("-- In CommWithSocket, received this payload: " + payload)

    client.connect(registerFlag ? 55557 : 55556, 'localhost', () => {
      client.write(payload)
      client.destroy()
    });

    client.on('error', function (err) {
      console.error(err);
      console.error("\nIt may be the case that nothing is listening on 55556/7!!")

      client.destroy()
      process.exit()
    })

}

// Send settings.py as json
app.get('/settings', (req, res) => {
  res.json(settings);
})

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + './../ui/build/index.html'));
})

// This function spawns a child process that run's 
// crow_caw which handles all the backend secret sharing 
function caw(){
  console.log('-- Spawning crow caw process')
  var process = spawn('python3', ['crow_caw.py'],
    {cwd: '../shamir/code/'})

  // Log crow_caw's stdout and send to dashboard
  process.stdout.on('data', function(data){
    console.log('-- Caw stdout: ' + data.toString())
    io.sockets.emit('testchannel', data.toString())
  })

  // Log crow_caw's stderr and redirect to our stderr
  process.stderr.on('data', function(data){
    console.error(data.toString())
  });

  // Log crow_caw's error and redirect to our stderr
  process.on('error', (err) => {
    console.error(err)
  })

}

// A bit of a hack but this function serves to 
// return specific details about the settings.py 
// which configures parts of our overall system
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

// Everytime the settings file is updated,
// re-read its data and transmit to dashboard
fs.watchFile(pathToSettings, () => {
  console.log('-- Settings file has changed');
  readSettingsFile();
  try {
    io.sockets.emit("SettingsUpdate", settings) 
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

const server = https.createServer(options, app)
  .listen(port, () => {
    readSettingsFile();

    process.env.DEV !== 'true' && caw();
    console.log('Connect to server at ' + ipAddresses + ':' + port)
  })

const io = socketIO(server);

io.on("connection", socket => {
  socket.on("disconnect", () => console.log('A client disconnected'));
  socket.on("qrchannel", (username, password, registerFlag) => CommWithSocket(username, password, registerFlag));
  socket.on("voiceChannel", (username, blob, registerFlag) => VoiceRecognition(username, blob, registerFlag));
  socket.on("SettingsUpdate", () => io.sockets.emit("SettingsUpdate", settings));
  socket.on("Register", (usr, full) => register(usr, full));
})

function VoiceRecognition(username, blob, registerFlag) {
  fs.writeFile('../voice-recognition/capture.ogg', blob, (err) => {
    if (!err) {

      var process = spawn('ffmpeg',
        ["-i", "./capture.ogg", "-vn", "./capture.wav", "-y"],
        { cwd: '../voice-recognition/' })

      process.on('close', () => {
        let scriptToRun = registerFlag ? "voice_reg.py" : "voice.py"
        var p2 = spawn('python3',
          [scriptToRun, username, "capture.wav"],
          { cwd: '../voice-recognition/' })
        
          p2.stdout.on('data', function (data) {
            console.log('-- In voice recognition, transcript is: ' + data.toString())
            //I think the script already deals with socket transmission
            //let payload = username + ':' + data.toString()
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

function register(username, fullname){
  console.log('-- Spawning register process')
  io.sockets.emit('Register')
  var process = spawn('python3', ['register_script.py', username, fullname],
    {cwd: '../shamir/code/'})

  // Log crow_caw's stdout and send to dashboard
  process.stdout.on('data', function(data){
    let msg = data.toString()
    console.log('-- Register stdout: ' + msg)
    if (msg.indexOf("SUCCESS" !== -1)){
      io.sockets.emit('Register')
    }
  })

  // Log crow_caw's stderr and redirect to our stderr
  process.stderr.on('data', function(data){
    console.error(data.toString())
  });

  // Log crow_caw's error and redirect to our stderr
  process.on('error', (err) => {
    console.error(err)
  })
}