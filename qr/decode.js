var Jimp = require("jimp");
var QrCode = require('qrcode-reader')
var fs = require('fs')
var net = require('net')
var Crypto = require('crypto-js')

//Read in image
var buffer = fs.readFileSync('./in.png')

//Jimp processes image
Jimp.read(buffer, function(err, image) {
    
    //leave if error
    if (err){
        return;
    }
    
    //new qr object
    var qr = new QrCode();
    
    //set function to call after decoding
    qr.callback = function(err, value) {
        if (err) {
            console.error(err);
            return;
        }
        
        //create new socket to listening localhost port
        s = new net.Socket()
        s.connect({host:'localhost', port:55556})
        
        //split qrcode into [username, value]
        let target = value.result.split(":")

        //write to socket [username:sha256(value)]
        s.write(target[0] + ":" + Crypto.enc.Base64.stringify(Crypto.SHA256(target[1])))
        s.end()
    };

    //decode qr
    qr.decode(image.bitmap);
});