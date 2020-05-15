import React from 'react'
import './keypad.css'
import Cookies from 'universal-cookie'
const cookies = new Cookies();

var pw = ''

export default class Keypad extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            opened: false || this.props.register
        };


        this.togglescreen = this.togglescreen.bind(this)
        this.enter = this.enter.bind(this)
        this.style_btn_press = this.style_btn_press.bind(this)
        this.clr = this.clr.bind(this)
        this.check_complete = this.check_complete.bind(this)
        this.update_cookie = this.update_cookie.bind(this)
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

    clr() {
        let btn = document.getElementById("clr");
        this.style_btn_press(btn);
        var entry = document.getElementById("entry");
        entry.innerHTML = '';
        pw = '';
        return 1;
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

    check_complete() {
        if (pw.length >= 6) {
            var http = new XMLHttpRequest();
            var url = 'https://' + window.location.hostname + ':3001' + '/auth';
            http.open('POST', url, true);

            //Send the proper header information along with the request
            http.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
            let shouldRegister = this.props.register ? 1 : 0;
            http.send(JSON.stringify({
                "username": shouldRegister ? "" : cookies.get('username'),
                "pw": pw,
                "register": shouldRegister }));

            pw = '';
            this.clr();
        }
    }


    style_btn_press(btn) {
        btn.style.boxShadow = "-2px -2px 12px 0 rgba(255,255,255,.5), 2px 2px 12px 0 rgba(0,0,0,.03)";
        btn.style.fontSize = "3.7em";
        btn.style.color = "grey";
        setTimeout(function () {
            btn.style.boxShadow = "-6px -6px 12px 0 rgba(255,255,255,.5), 12px 12px 12px 0 rgba(0,0,0,.03)";
            btn.style.fontSize = "4em";
            btn.style.color = "black";
        }, 250);
    }

    enter(i) {
        var entry = document.getElementById("entry");
        let btn = document.getElementById(i);
        this.style_btn_press(btn);
        pw += i.toString();
        entry.innerHTML += '*'
        this.check_complete();
        return 1;
    }



    render() {
        const opened = this.state.opened
        return (
            <div className='outer'>
                {!opened && this.WelcomePage()} 

                {opened &&
                    <div id="scr_2">
                        <h1 id="entry" className="entry"></h1>

                        <div className="grid">
                            <div className="row">
                                <button className="cell" id="1" onClick={() => this.enter(1)}>1</button>
                                <button className="cell" id="2" onClick={() => this.enter(2)}>2</button>
                                <button className="cell" id="3" onClick={() => this.enter(3)}>3</button>
                            </div>{}
                            <div className="row">{}
                                <button className="cell" id="4" onClick={() => this.enter(4)}>4</button>
                                <button className="cell" id="5" onClick={() => this.enter(5)}>5</button>
                                <button className="cell" id="6" onClick={() => this.enter(6)}>6</button>
                            </div>{}
                            <div className="row">{}
                                <button className="cell" id="7" onClick={() => this.enter(7)}>7</button>
                                <button className="cell" id="8" onClick={() => this.enter(8)}>8</button>
                                <button className="cell" id="9" onClick={() => this.enter(9)}>9</button>
                            </div>
                            <div className="row">
                                <div className="cell hidden"></div>
                                <button className="cell" id="0" onClick={() => this.enter(0)}>0</button>
                                <button className="cell" id="clr" onClick={this.clr}>Clear</button>
                            </div>
                        </div>
                    </div>
                }
            </div>
        )
    }

}

