import React, { Component } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard'
import Keypad from './pages/Keypad'

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  
  Switch() {
    switch(this.state["id"]){
      case 'auth':
        return <Dashboard />;
      case 'keypad':
        return <Keypad />;
      default:
        return <h1>Unrecognized Node Type...</h1>
    }
  }


  callAPI() {
    fetch('http://localhost:3001/')
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
