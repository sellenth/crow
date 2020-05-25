const express  = require('express')
const app      = express()
const https    = require('https')
const path     = require('path')
const cors     = require('cors')
const sha256   = require('js-sha256').sha256
const fs       = require('fs')
const net      = require('net');
const spawn    = require('child_process').spawn;
const client   = new net.Socket();
const port     = process.env.PORT || 3001
const devOut   = require('debug')('dev')
const socketIO = require('socket.io')
const settings = {}
const cookieParser   = require('cookie-parser')
const pathToSettings = '../shamir/code/settings.py';
const { createMultiSocket } = require('./challenge')

let MULT_ADDR = ''
let MULT_PORT = 0

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
// ingested by crow_caw or to 55557 where it is used
// in the register_script.py
function CommWithSocket(username, password, registerFlag){
    if (password.length > 66){
      io.emit("ErrChannel", "Password is too long to be securely hashed, try a shorter one")
      return
    }
    devOut("-- The username is: " + username + ' and the password is: ' + password)
    let payload

    // When registering a user we send only a hash of their password
    if (registerFlag) {
      console.log("-- User is being registered")
      let pw_hash = sha256(password)
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
      console.error("\nIt may be the case that nothing is listening on 55556/7!")
      client.destroy()
      process.exit()
    })

}

// Send settings.py as json
app.get('/settings', (req, res) => {
  res.json(settings);
})

// Serve the finished React build document on /
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

    else if (line.includes("MULT_ADDR")) {
      MULT_ADDR = line.substring(
        line.indexOf("'") + 1,
        line.lastIndexOf("'"))
    }

    else if (line.includes("MULT_PORT")) {
      MULT_PORT = line.substring(
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

// This function takes the IPs addresses of the local machine
// (it makes it easier to connect to the docker containers) 
function returnIPs(){
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
  return ipAddresses
}

const server = https.createServer(options, app)
  .listen(port, () => {
    readSettingsFile();
    process.env.DEV !== 'true' && caw();
    createMultiSocket(MULT_ADDR, MULT_PORT)
    console.log('Connect to server with one of the following addresses ' + returnIPs())
    console.log('Use the port ' + port)
  })

// Create the socketIO server
const io = socketIO(server);

// These are the channels that the socketIO server listens on
io.on("connection", socket => {
  // Log when a user disconnects from the site
  socket.on("disconnect", () => console.log('-- A client disconnected'));

  // qrchannel takes data from qr scan or generated qr
  // and sends it to crow_caw or register_script
  socket.on("qrchannel", (username, password, registerFlag) => CommWithSocket(username, password, registerFlag));

  // voice channel takes an audio data blob 
  // and sends it to voice_reg.py or voice.py
  socket.on("voiceChannel", (username, blob, registerFlag) => VoiceRecognition(username, blob, registerFlag));

  // When socket hears a call for settingsUpdate, sends the newest version of settings
  socket.on("SettingsUpdate", () => io.sockets.emit("SettingsUpdate", settings));

  // When socket hears register, initiate the register_script.py
  socket.on("Register", (usr, full) => register(usr, full));
})

// This function first spawns ffmpeg to convert the blob
// into a more widely useable form and then spawns one 
// voice_reg.py or voice.py, using the converted audio
// file as input
function VoiceRecognition(username, blob, registerFlag) {
  // write the blob to file
  fs.writeFile('../voice-recognition/capture.ogg', blob, (err) => {
    if (!err) {

      // -i option grabs input files
      // -vn skip inclusion of video in output
      // -y overwrite previous versions of output .wav
      var process = spawn('ffmpeg',
        ["-i", "./capture.ogg", "-vn", "./capture.wav", "-y"],
        { cwd: '../voice-recognition/' })

      // When the conversion is complete
      process.on('close', () => {
        // Decide which script to run
        let scriptToRun = registerFlag ? "voice_reg.py" : "voice.py"
        // spawn python3 with that script and supply the username
        // that the transcription will be send with
        var p2 = spawn('python3',
          [scriptToRun, username, "capture.wav"],
          { cwd: '../voice-recognition/' })
        
          p2.stdout.on('data', function (data) {
            console.log('-- In voice recognition, transcript is: ' + data.toString())
            io.sockets.emit('voiceChannel', data.toString())
          })

          process.stderr.on('data', function (data) {
            console.error(data.toString())
          });
      })
    }
  })
}


// spawn the register script for a new user
// given their username and fullname
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