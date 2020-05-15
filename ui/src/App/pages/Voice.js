import React, { Component } from 'react'
import { ReactMic } from 'react-mic';
import { MdFiberManualRecord } from 'react-icons/md'
import { IconContext } from "react-icons";
import { FaStop } from 'react-icons/fa'
import Cookies from 'universal-cookie'
import './Voice.css'
const cookies = new Cookies();


export default class Voice extends Component {
    constructor(props) {
        super(props);
        this.state = {
            record: false,
            opened: false || this.props.register
        }
        
        this.onStop = this.onStop.bind(this)
    }

    toggleRecording = () => {
        this.setState({ record: !this.state.record });
        let box = document.getElementById('play')
        box.style.boxShadow = "-2px -2px 12px 0 rgba(255,255,255,.5), 2px 2px 12px 0 rgba(0,0,0,.03)";
        box.style.fontSize = "3.7em";
        box.style.color = "grey";
        setTimeout(function () {
            box.style.boxShadow = "-6px -6px 12px 0 rgba(255,255,255,.5), 12px 12px 12px 0 rgba(0,0,0,.03)";
            box.style.fontSize = "4em";
            box.style.color = "black";
        }, 250);
    }

    togglescreen() {
        const { opened } = this.state;
        this.setState({
            opened: !opened,
        })
    }


    update_cookie = event => {
        event.preventDefault();

        let username = document.getElementById('i_username').value

        cookies.set('username', username)
        this.togglescreen();
    }

    componentDidMount() {

    }

    onStop(recordedBlob) {
        console.log('recordedBlob is: ', recordedBlob);
        let register = this.props.register ? 1 : 0;
        this.props.socket.emit('voiceChannel', cookies.get('username'), recordedBlob.blob, register);
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
                            <form onSubmit={this.update_cookie}>
                                <input id="i_username" type="text" name="username" autoFocus />
                            </form>
                        </div>
                    </div>
                </div>
            </div >
        )
    }

    render(){

        return (
            <>
                {!this.state.opened && this.WelcomePage()}
                {this.state.opened &&
                    <>
                        <div className="buttonsBar" style={{
                            height: '100%',
                            width: '100%',
                            justifyContent: 'center',
                            alignItems: 'center',
                            position: 'absolute',
                            display: 'flex',
                        }}>
                            <button
                                id="play"
                                onClick={this.toggleRecording}
                                className="start play-stop"
                                type="button">
                                {!this.state.record &&
                                    <IconContext.Provider value={{ color: "#CC0004", size: '15vw', className: 'record-button' }}>
                                        <MdFiberManualRecord />
                                    </IconContext.Provider>
                                }
                                {this.state.record &&
                                    <IconContext.Provider value={{ color: "#999", size: '10vw' }}>
                                        <FaStop />
                                    </IconContext.Provider>
                                }
                            </button>
                        </div>
                        <div style={{
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'flex-end',
                            alignItems: 'center',
                            height: '100%'
                        }}>
                            <ReactMic
                                record={this.state.record}
                                visualSetting="frequencyBars"
                                className="sound-wave"
                                onStop={this.onStop}
                                strokeColor="#000000"
                                backgroundColor="#EEEEEE" />
                        </div>
                    </>
                }
            </>
        )
    }
}