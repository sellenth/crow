import React, { Component } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard'
import Keypad from './pages/Keypad'
import socketIOClient from 'socket.io-client'
import 'bootstrap/dist/css/bootstrap.min.css';


const socket = socketIOClient(window.location.href)

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
      default:
        return <h1>Unrecognized Node Type...</h1>
    }
  }


  callAPI() {
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
