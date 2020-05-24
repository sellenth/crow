/* eslint-disable jsx-a11y/no-autofocus */
import React, { Component } from 'react';
import { ReactMic } from 'react-mic';
import { MdFiberManualRecord } from 'react-icons/md';
import { IconContext } from 'react-icons';
import { FaStop } from 'react-icons/fa';
import Cookies from 'universal-cookie';
import PropTypes from 'prop-types';
import './Voice.css';

const cookies = new Cookies();

export default class Voice extends Component {
  constructor(props) {
    super(props);
    const { register } = this.props;
    this.state = {
      record: false,
      opened: false || register,
    };

    this.onStop = this.onStop.bind(this);
  }

  // When the recording is stopped, send the voice blob
  // to the backend for processing
  onStop(recordedBlob) {
    const { register, socket } = this.props;
    const shouldRegister = register ? 1 : 0;
    socket.emit('voiceChannel', cookies.get('username'), recordedBlob.blob, shouldRegister);
  }

    // toggle between recording and not recording
    // update the button style to simulate button being pressed
    toggleRecording = () => {
      const { record } = this.state;
      this.setState({ record: !record });
      const box = document.getElementById('play');
      box.style.boxShadow = '-2px -2px 12px 0 rgba(255,255,255,.5), 2px 2px 12px 0 rgba(0,0,0,.03)';
      box.style.fontSize = '3.7em';
      box.style.color = 'grey';
      setTimeout(() => {
        box.style.boxShadow = '-6px -6px 12px 0 rgba(255,255,255,.5), 12px 12px 12px 0 rgba(0,0,0,.03)';
        box.style.fontSize = '4em';
        box.style.color = 'black';
      }, 250);
    }

    // Store username in cookie
    updateCookie = (event) => {
      event.preventDefault();

      const username = document.getElementById('i_username').value;

      cookies.set('username', username);
      this.togglescreen();
    }


    // Toggle between welcome screen and record screen
    togglescreen() {
      const { opened } = this.state;
      this.setState({
        opened: !opened,
      });
    }

    WelcomePage() {
      return (
        <div id="scr_1">
          <div className="centered" id="welcome">
            <div className="window">
              <div className="w_header">
                <h1>Howdy!</h1>
              </div>
              <div className="w_content">
                <h2>Please enter your username:</h2>
                <form onSubmit={this.updateCookie}>
                  <input id="i_username" type="text" name="username" autoFocus />
                </form>
              </div>
            </div>
          </div>
        </div>
      );
    }

    render() {
      const { opened, record } = this.state;
      return (
        <>
          {!opened && this.WelcomePage()}
          {opened
                    && (
                    <>
                      <div
                        className="buttonsBar"
                        style={{
                          height: '100%',
                          width: '100%',
                          justifyContent: 'center',
                          alignItems: 'center',
                          position: 'absolute',
                          display: 'flex',
                        }}
                      >
                        <button
                          id="play"
                          onClick={this.toggleRecording}
                          className="start play-stop"
                          type="button"
                        >
                          {!record
                                    && (
                                    <IconContext.Provider value={{ color: '#CC0004', size: '15vw', className: 'record-button' }}>
                                      <MdFiberManualRecord />
                                    </IconContext.Provider>
                                    )}
                          {record
                                    && (
                                    <IconContext.Provider value={{ color: '#999', size: '10vw' }}>
                                      <FaStop />
                                    </IconContext.Provider>
                                    )}
                        </button>
                      </div>
                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'flex-end',
                        alignItems: 'center',
                        height: '100%',
                      }}
                      >
                        <ReactMic
                          record={record}
                          visualSetting="frequencyBars"
                          className="sound-wave"
                          onStop={this.onStop}
                          strokeColor="#000000"
                          backgroundColor="#EEEEEE"
                        />
                      </div>
                    </>
                    )}
        </>
      );
    }
}

Voice.propTypes = {
  socket: PropTypes.shape.isRequired,
  register: PropTypes.string.isRequired,
};
