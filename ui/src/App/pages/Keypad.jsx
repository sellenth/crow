/* eslint-disable jsx-a11y/heading-has-content */
/* eslint-disable jsx-a11y/no-autofocus */
import React from 'react';
import './keypad.css';
import Cookies from 'universal-cookie';
import PropTypes from 'prop-types';

const cookies = new Cookies();

let pw = '';

export default class Keypad extends React.Component {
  constructor(props) {
    super(props);
    const { register } = this.props;
    this.state = {
      opened: false || register,
    };


    this.togglescreen = this.togglescreen.bind(this);
    this.enter = this.enter.bind(this);
    this.styleBtnPress = this.styleBtnPress.bind(this);
    this.clr = this.clr.bind(this);
    this.checkComplete = this.checkComplete.bind(this);
    this.updateCookie = this.updateCookie.bind(this);
  }

    // Set the cookie to contain the current user's username
    updateCookie = (event) => {
      event.preventDefault();

      const username = document.getElementById('i_username').value;

      cookies.set('username', username);
      this.togglescreen();
    }

    // used to toggle between welcome screen and keypad screen
    togglescreen() {
      const { opened } = this.state;
      this.setState({
        opened: !opened,
      });
    }


    // clear the password and placeholder asterisks
    clr() {
      const btn = document.getElementById('clr');
      this.styleBtnPress(btn);
      const entry = document.getElementById('entry');
      entry.innerHTML = '';
      pw = '';
      return 1;
    }

    // Used to grab the username from user
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

    // Called whenever a digit is added to the PIN
    checkComplete() {
      const { register } = this.props;
      // if the PIN is the desired length, send it to the backend
      if (pw.length >= 6) {
        const http = new XMLHttpRequest();
        const url = `https://${window.location.hostname}:3001/auth`;
        http.open('POST', url, true);

        // Send the proper header information along with the request
        http.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
        const shouldRegister = register ? 1 : 0;
        http.send(JSON.stringify({
          username: shouldRegister ? '' : cookies.get('username'),
          pw,
          register: shouldRegister,
        }));

        // Clear the password
        pw = '';
        // reset placeholder asterisks back to 0
        this.clr();
      }
    }

    // This function changes subtle style options and
    // reverts them back after .25 seconds to simulate the
    // feel of depressing a button
    styleBtnPress(btn) {
      btn.style.boxShadow = '-2px -2px 12px 0 rgba(255,255,255,.5), 2px 2px 12px 0 rgba(0,0,0,.03)';
      btn.style.fontSize = '3.7em';
      btn.style.color = 'grey';
      setTimeout(() => {
        btn.style.boxShadow = '-6px -6px 12px 0 rgba(255,255,255,.5), 12px 12px 12px 0 rgba(0,0,0,.03)';
        btn.style.fontSize = '4em';
        btn.style.color = 'black';
      }, 250);
    }

    // Called whenever a keypad button is pressed
    enter(i) {
      const entry = document.getElementById('entry');
      const btn = document.getElementById(i);
      // change size of button and add shadow for effect
      this.styleBtnPress(btn);
      // append the button's number value to the password
      pw += i.toString();
      // indicate to the user how many digits they have entered
      entry.innerHTML += '*';
      // check if the user has submitted enough digits to complete the PIN
      this.checkComplete();
      return 1;
    }


    render() {
      const { opened } = this.state;
      return (
        <div className="outer">
          {!opened && this.WelcomePage()}

          {opened
                    && (
                    <div id="scr_2">
                      <h1 id="entry" className="entry" />

                      <div className="grid">
                        <div className="row">
                          <button type="button" className="cell" id="1" onClick={() => this.enter(1)}>1</button>
                          <button type="button" className="cell" id="2" onClick={() => this.enter(2)}>2</button>
                          <button type="button" className="cell" id="3" onClick={() => this.enter(3)}>3</button>
                        </div>
                        {}
                        <div className="row">
                          {}
                          <button type="button" className="cell" id="4" onClick={() => this.enter(4)}>4</button>
                          <button type="button" className="cell" id="5" onClick={() => this.enter(5)}>5</button>
                          <button type="button" className="cell" id="6" onClick={() => this.enter(6)}>6</button>
                        </div>
                        {}
                        <div className="row">
                          {}
                          <button type="button" className="cell" id="7" onClick={() => this.enter(7)}>7</button>
                          <button type="button" className="cell" id="8" onClick={() => this.enter(8)}>8</button>
                          <button type="button" className="cell" id="9" onClick={() => this.enter(9)}>9</button>
                        </div>
                        <div className="row">
                          <div className="cell hidden" />
                          <button type="button" className="cell" id="0" onClick={() => this.enter(0)}>0</button>
                          <button type="button" className="cell" id="clr" onClick={this.clr}>Clear</button>
                        </div>
                      </div>
                    </div>
                    )}
        </div>
      );
    }
}

Keypad.propTypes = {
  register: PropTypes.string.isRequired,
};
