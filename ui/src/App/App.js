import React, { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Dashboard from './pages/Dashboard'
import Keypad from './pages/Keypad'
import Qr from './pages/Qr'
import Voice from './pages/Voice'
import socketIOClient from 'socket.io-client'

// Conect to the nodeJS server's socket
const socket = socketIOClient('https://' + window.location.hostname + ':' + 3001, {secure: true})

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      registerUsername: '',
      numRegistered: 0,
      registerMode: 0,
      threshold: 0,
      total:     0,
      id:   "none"
    };
    this.registerHandler = this.registerHandler.bind(this)
  }
  
  Switch() {
    if (this.state.registerMode){
      switch(this.state.numRegistered){
        case 1:
          return <Keypad register={'true'}/>
        case 2:
          return <Qr username={this.state.registerUsername} register={'true'} socket={socket} />
        case 3:
          return <Voice register={'true'} socket={socket} />
      }
    }
    else{
      switch(this.state["id"]){
        case 'auth':
          return <Dashboard 
          socket={socket}
          registerHandler={this.registerHandler}
          threshold={this.state.threshold}
          total={this.state.total}/>;
        case 'web':
          return <Keypad />;
        case 'qr':
          return <Qr socket={socket}/>;
        case 'voice':
          return <Voice socket={socket}/>;
        case 'register':
        default:
          return <h1>Unrecognized Node Type...</h1>
      }
    }
  }

  registerHandler(username, fullname) {
    this.setState({
      registerMode: 1,
      registerUsername: username
    })
    socket.emit("Register", username, fullname)
  }

  componentDidMount() {
    socket.emit("SettingsUpdate")
    socket.on("SettingsUpdate", (settingsJSON) => {
      this.setState(settingsJSON)
    })
    socket.on("Register", () => {
      if (this.state.numRegistered >= this.state.total){
        this.setState({
          registerUsername: '',
          registerMode: 0,
          numRegistered: 0
        })
      }
      this.setState({
        numRegistered: this.state.numRegistered + 1
      })
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
