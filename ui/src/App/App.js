import React, { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Dashboard from './pages/Dashboard'
import Keypad from './pages/Keypad'
import Qr from './pages/Qr'
import Voice from './pages/Voice'
import socketIOClient from 'socket.io-client'


const socket = socketIOClient(window.location.href)
// CHANGE THIS IN DEV
//const socket = socketIOClient('http://localhost:3001')

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {};
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

  callAPI() {
// CHANGE THIS IN DEV
    //fetch('http://localhost:3001/settings')
    fetch('/settings')
      .then(response => response.json())
      .then((jsonData) => {
        this.setState(jsonData)
      })
      .catch((error) => {
        console.error(error)
    })
  }

  componentDidMount() {
    this.callAPI();
    socket.on("SettingsUpdate", () => {
      console.log('got socket update')
      this.callAPI();
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
