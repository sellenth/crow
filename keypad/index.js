const express = require('express')
const bodyParser = require('body-parser')
const app = express()
const http = require('http')
const path = require('path')
const fs = require('fs')
const net = require('net');
const client = new net.Socket();
const cookieParser = require('cookie-parser')
const port = process.env.PORT || 3000

app.use(express.static('public'))
app.use(bodyParser.json())
app.use(cookieParser())


app.post('/auth', (req, res) => {
  let username = req.cookies.username;
  let pw = req.body.pw;

  client.connect(55556, 'localhost', function () {
    client.write(username + ':' + pw);
  })
  // TODO: send response to client
})

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
  console.log(settings)

} catch (err){
  console.log(err)
  console.log("\n\nFailed to read node settings, aborting");
  process.exit(1)
}

const server = http.createServer(app)
    .listen(port, () => {
        console.log('server running on port ' + port)
    })
