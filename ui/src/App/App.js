import React, { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Dashboard from './pages/Dashboard'
import Keypad from './pages/Keypad'
import Qr from './pages/Qr'
import Voice from './pages/Voice'
import socketIOClient from 'socket.io-client'

// Conect to the nodeJS server's socket
const socket = socketIOClient(window.location.hostname + ':' + 3001)

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      threshold: 0,
      total:     0,
      id:   "none"
    };
  }
  
  Switch() {
    switch(this.state["id"]){
      case 'auth':
        return <Dashboard socket={socket} threshold={this.state.threshold} total={this.state.total}/>;
      case 'web':
        return <Keypad />;
      case 'qr':
        return <Qr socket={socket}/>;
      case 'voice':
        return <Voice socket={socket}/>;
      default:
        return <h1>Unrecognized Node Type...</h1>
    }
  }

  componentDidMount() {
    socket.emit("SettingsUpdate")
    socket.on("SettingsUpdate", (settingsJSON) => {
      this.setState(settingsJSON)
    })
  }

  render() {
    return (
      <div className="App">
        {this.Switch()}
      </div>
    );
  }
}

export default App;
