const express = require('express')
const app = express()
const http = require('http')
const path = require('path')
const fs = require('fs')
const net = require('net');
const client = new net.Socket();
const cookieParser = require('cookie-parser')
const port = 3001

// Middlewares
app.set("views", path.join(__dirname, "views"))
// Might not end up using this app.set("view engine", "jade")
app.use(express.static('public'))
app.use(express.json())
app.use(cookieParser())


// Authentication route
app.post('/auth', (req, res) => {
  const username = req.cookies.username;
  const pw = req.body.pw;

  client.connect(55556, 'localhost', function () {
    client.write(username + ':' + pw);
  })

  client.on('error', function(err){
    console.log("Error: "+err.message);
})

  // TODO: send response to client
})

// Serve correct homescreen for node type
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + '/public/html/index.html'));
})

function parseSettings(settingsFile){
  let settings = {};
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

try {
  let settingsFile = fs.readFileSync('../shamir/code/settings.py', 'utf8').split('\n');
  var settings = parseSettings(settingsFile);
} catch (err){
  console.log(err)
  console.log("\n\nFailed to read node settings, aborting");
  process.exit(1)
}

const server = http.createServer(app)
    .listen(port, () => {
        console.log('server running on port ' + port)
    })
