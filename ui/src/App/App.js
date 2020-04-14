import React, { Component } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard'
import Keypad from './pages/Keypad'
import socketIOClient from 'socket.io-client'

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  
  Switch() {
    switch(this.state["id"]){
      case 'auth':
        return <Dashboard />;
      case 'web':
        return <Keypad />;
      default:
        return <h1>Unrecognized Node Type...</h1>
    }
  }


  callAPI() {
    fetch('http://localhost:3001/')
      .then(response => response.json())
      .then((jsonData) => {
        console.log(jsonData)
        this.setState(jsonData)
      })
      .catch((error) => {
        console.error(error)
    })
  }

  componentDidMount() {
    this.callAPI();
    const socket = socketIOClient('http://localhost:3001')
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
