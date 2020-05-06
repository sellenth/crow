import React, { Component } from 'react'
import QrReader from 'react-qr-reader'
import './Qr.css'


export default class Qr extends Component {
    state = {
        result: 'No result'
    }

    handleScan = data => {
        if (data && this.state.result !== data) {
            console.log(data)
            this.setState({
                result: data
            })
            this.props.socket.emit('qrchannel', data)
            setTimeout(() => {
                this.setState({
                    result: 'No result'
                })
            }, 5000)
        }
    }

    handleError = err => {
        console.error(err)
    }

    render() {
        return (
            <div style={{
                height: '90%',
                display: "flex",
                justifyContent: "center",
                flexDirection: "column",
                alignItems: "center"
            }}>
                {this.state.result === 'No result' &&
                    <h1>Scan your QR Code</h1>}
                {this.state.result !== 'No result' &&
                    <h1>QR scan has been received!</h1>}
                <QrReader
                    delay={300}
                    onError={this.handleError}
                    onScan={this.handleScan}
                    style={{ width: '40%' }}
                />
            </div>
        )
    }
}