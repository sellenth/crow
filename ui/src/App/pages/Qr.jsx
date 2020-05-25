import React, { Component } from 'react';
import QrReader from 'react-qr-reader';
import { FaArrowCircleRight } from 'react-icons/fa';
import PropTypes from 'prop-types';

import QRCode from 'qrcode.react';

import './Qr.css';

export default class Qr extends Component {
  constructor(props) {
    super(props);
    const { username } = this.props;
    // http://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid-in-javascript
    const password = Math.random().toString(36).substring(2, 15)
      + Math.random().toString(36).substring(2, 15);
    this.state = {
      result: 'No result',
      code: `${username}:${password}`,
    };
    this.registerQR = this.registerQR.bind(this);
  }

    // if the current scan returns fresh value to the
    // component state, decompose it into username and
    // password parts and send it to the backend for processing
    // after 5 seconds, delete scan from state
    handleScan = (data) => {
      const { result } = this.state;
      const { register, socket } = this.state;

      if (data && result !== data) {
        this.setState({
          result: data,
        });
        const colonPos = data.indexOf(':');
        const username = data.slice(0, colonPos);
        const password = data.slice(colonPos + 1);
        const shouldRegister = register ? 1 : 0;
        socket.emit('qrchannel', username, password, shouldRegister);
        setTimeout(() => {
          this.setState({
            result: 'No result',
          });
        }, 5000);
      }
    }

    // Log out any error messages that arise from the scanning process
    // handleError = (err) => {
    //  console.error(err);
    // }

    // this function will take the username and generated
    // password from the qr code and send it to the back-
    // end for registration
    registerQR() {
      const { code } = this.state;
      const { socket } = this.props;
      const colonPos = code.indexOf(':');
      const username = code.slice(0, colonPos);
      const password = code.slice(colonPos + 1);
      socket.emit('qrchannel', username, password, 1);
    }

    // If in register mode, display the generated QR code
    // otherwise, scan the user's webcam for QR codes
    render() {
      const { code, result } = this.state;
      const { register } = this.props;
      return (
        <>
          {register
                    && (
                    <div className="QRcontainer">
                      <QRCode
                        style={{
                          margin: '10% auto 5% auto',
                          width: '50vh',
                          maxWidth: '50%',
                          height: '50%',
                        }}
                        value={code}
                      />
                      <h2 style={{ marginBottom: '3%' }}>Save this QR and continue</h2>
                      <FaArrowCircleRight className="clickable" onClick={this.registerQR} size={48} />
                    </div>
                    )}
          {!register
                    && (
                    <div style={{
                      height: '90%',
                      display: 'flex',
                      justifyContent: 'center',
                      flexDirection: 'column',
                      alignItems: 'center',
                    }}
                    >
                      {result === 'No result'
                            && <h1 style={{ fontSize: '4em' }}>Scan your QR Code</h1>}
                      {result !== 'No result'
                            && <h1 style={{ fontSize: '4em' }}>QR scan has been received!</h1>}
                      <QrReader
                        delay={300}
                        onError={this.handleError}
                        onScan={this.handleScan}
                        style={{ width: '40%' }}
                      />
                    </div>
                    )}
        </>
      );
    }
}

Qr.propTypes = {
  socket: PropTypes.shape.isRequired,
  register: PropTypes.string.isRequired,
  username: PropTypes.string.isRequired,
};
