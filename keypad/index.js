const express = require('express')
const app = express()
const http = require('http')
const path = require('path')
const net = require('net')
const client = new net.Socket();
const cookieParser = require('cookie-parser')
const fs = require('fs')
const port = 3000

app.use(express.static('public'))
app.use(cookieParser())

app.post('/auth:pw', (req, res) => {
  let username = req.cookies.username
  let pw = req.params.pw;

  client.connect(55556, '127.0.0.1', () => {
    client.write(username + ':' + pw);
  });
  res.status(200).send();
})

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + '/public/html/index.html'));
})

const server = http.createServer(app)
    .listen(port, () => {
        console.log('server running at ' + port)
    })
