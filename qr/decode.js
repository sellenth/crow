var Jimp = require("jimp");
var QrCode = require('qrcode-reader')
var fs = require('fs')
var net = require('net')
var buffer = fs.readFileSync('./in.png')


Jimp.read(buffer, function(err, image) {
    if (err) {
        console.error(err);
        // TODO handle error
    }
    var qr = new QrCode();
    qr.callback = function(err, value) {
        if (err) {
            console.error(err);
            // TODO handle error
        }
        s = new net.Socket()
        s.connect({host:'localhost', port:55556})
        s.write(value.result)
        s.end()
    };
    qr.decode(image.bitmap);
});