const dgram    = require("dgram");
const crypto = require('crypto');
var fs = require('fs');
require.extensions['.pub'] = function (module, filename) {
    module.exports = fs.readFileSync(filename, 'utf8');
};


function createKeyhash(){
    const pubKey = require("../shamir/assets/local.pub");
    const shaHash = crypto.createHmac('sha256', pubKey).digest()
    const keyhash = new Buffer(shaHash, 'ascii')
    return keyhash
}

function createChallengeMsg(keyhash){
    const authPubKey = require("../shamir/assets/auth.pub");
    const buff = Buffer.concat([Buffer.from('who?:'), createKeyhash()])
    return crypto.publicEncrypt(
        authPubKey,
        buff)
}

function createPayloadMsg(data, payload){
    const authPubKey = require("../shamir/assets/auth.pub");
    const buff = new Buffer("you!:" + data + ":" + payload)
    return crypto.publicEncrypt(
        authPubKey,
        buff
    )
}

function generalSocket(port){
    const net = require('net')
    const socket = new net.Socket();
    socket.connect(port, 'localhost')
    socket.on('connect', () => { 
        console.log(`Socket on port ${port} connected successfully`)})
    socket.on('error', () => {
        console.log(`Error creating socket on port ${port}, exiting`)
        process.exit()
    })
    return socket;
}

function decrypteWithPrivateKey(encrypted){
    const privKey = fs.readFileSync('../shamir/assets/local', 'utf8')
    return crypto.privateDecrypt(privKey, encrypted)
}

exports.returnAddr = (MULTICAST_ADDR, PORT, cb) => {
    const multicastSocket = createMultiSocket(MULTICAST_ADDR, PORT)
    const generalSocket = createSocket(55551)
    const keyhash = createKeyhash();
    const multiChallenge = createChallengeMsg(keyhash);
    multicastSocket.send(multiChallenge)

    generalSocket.on('data', (data) => {
        const decryptedBuf = decrypteWithPrivateKey(data)
        const decryptedStr = decryptedBuf.toString('ascii')
        multicastSocket.send(createPayloadMsg(decryptedStr, ))
    })



}

exports.createMultiSocket = (MULTICAST_ADDR, PORT) => {
    const multicastSocket = dgram.createSocket({ type: "udp4", reuseAddr: true})
    multicastSocket.bind(parseInt(PORT))
    multicastSocket.on("listening", function() {
        multicastSocket.addMembership(MULTICAST_ADDR);

        //setInterval(sendMessage, 2500);
        const address = multicastSocket.address();
        console.log(
          `UDP socket listening on ${address.address}:${address.port} pid: ${
            process.pid
          }`
        );
      });
      
      function sendMessage() {
        const message = Buffer.from(`Message from process ${process.pid}`);
        multicastSocket.send(message, 0, message.length, PORT, MULTICAST_ADDR, function() {
          console.info(`Sending message "${message}"`);
        });
      }
      
      multicastSocket.on("message", function(message, rinfo) {
        console.info(`Message from: ${rinfo.address}:${rinfo.port} - ${message}`);
      });

      return multicastSocket;
}