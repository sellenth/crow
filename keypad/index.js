const express = require('express')
const app = express()
const http = require('http')
const path = require('path')
const fs = require('fs')
const port = 3000

app.use(express.static('public'))

app.post('/auth:pw', (req, res) => {
  let username = req.headers.cookie;
  let pw = req.params.pw;
  var spawn = require("child_process").spawn;
  var process = spawn('python3',["./shamir_client.py",
    "r3k",
    "web",
    pw]);

    //req.query.firstname,
    //req.query.lastname] );

  process.stdout.on('data', function(data) {
    console.log(data.toString());
        res.send(data.toString());
  } )
})

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + '/public/html/index.html'));
})

const server = http.createServer(app)
  .listen(port, () => {
    console.log('server running at ' + port)
  })
