import React from 'react'
//import './Dashboard.css'

export default class Dashboard extends React.Component {
    componentDidMount(){
        const socket = this.props.socket;
        socket.on('testchannel', (data) => {
            console.log(data)
        })
    }

    render(){
        return <h1>Welcome back! {this.props.threshold}</h1>;
    }
  }