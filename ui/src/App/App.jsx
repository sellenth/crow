import React, { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import socketIOClient from 'socket.io-client';
import Dashboard from './pages/Dashboard';
import Keypad from './pages/Keypad';
import Qr from './pages/Qr';
import Voice from './pages/Voice';
import Loading from './pages/Loading';

// Connect to the nodeJS server's socket
const socket = socketIOClient(`https://${window.location.hostname}:${3001}`, { secure: true });

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      dashboardState: null,
      registerUsername: '',
      numRegistered: 0,
      registerMode: 0,
      threshold: 0,
      total: 0,
      id: 'none',
    };
    this.registerHandler = this.registerHandler.bind(this);
    this.liftstate = this.liftstate.bind(this);
  }

  componentDidMount() {
    const { numRegistered, total } = this.state;
    socket.emit('SettingsUpdate');
    socket.on('SettingsUpdate', (settingsJSON) => {
      this.setState(settingsJSON);
    });
    socket.on('Register', () => {
      if (numRegistered >= total) {
        this.setState({
          registerUsername: '',
          registerMode: 0,
          numRegistered: 0,
        });
      }
      this.setState({
        numRegistered: numRegistered + 1,
      });
    });
  }

  liftstate(s) {
    this.setState({
      dashboardState: s,
    });
  }

  Switch() {
    const {
      id, registerMode, numRegistered, registerUsername, dashboardState, threshold, total,
    } = this.state;
    if (registerMode) {
      switch (numRegistered) {
        case 1:
          return <Keypad register="true" />;
        case 2:
          return <Qr username={registerUsername} register="true" socket={socket} />;
        case 3:
          return <Voice register="true" socket={socket} />;
        default:
          return <h1>Attempted to register node type that does not exit</h1>;
      }
    } else {
      switch (id) {
        case 'auth':
          return (
            <Dashboard
              savedState={dashboardState}
              liftState={this.liftstate}
              socket={socket}
              registerHandler={this.registerHandler}
              threshold={parseInt(threshold, 10)}
              total={parseInt(total, 10)}
            />
          );
        case 'web':
          return <Keypad />;
        case 'qr':
          return <Qr socket={socket} />;
        case 'voice':
          return <Voice socket={socket} />;
        case 'register':
        default:
          return <h1>Unrecognized Node Type...</h1>;
      }
    }
  }

  registerHandler(username, fullname) {
    this.setState({
      registerMode: 1,
      registerUsername: username,
    });
    socket.emit('Register', username, fullname);
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
