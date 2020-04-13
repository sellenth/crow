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
})

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname + '/public/html/index.html'));
})

const server = http.createServer(app)
    .listen(port, () => {
        console.log('server running on port ' + port)
    })
