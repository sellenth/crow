import React from 'react'
import { GiSpeaker, GiCyborgFace, GiLockedFortress } from 'react-icons/gi'
import { FaBarcode, FaGlobe, FaServer } from 'react-icons/fa'
import { IconContext } from "react-icons";
import { Container, Row, Col } from 'react-bootstrap'

import './Dashboard.css'

{/* 
    print("Sending Update to Client Node")
    print("Got share")
    print("Node registered:   " + data[1])
	print("Sending New Share to other Auth Nodes") 
	print("Recieved Share from Client Node")
    print(share["id"] + " has submitted " + str(share["num_shares"]) + " shares!")
    print(res["name"] + " (" + res["username"] + ")" + " is Authorized!")
    kill -9 $(sudo lsof -t -i:55557)
*/}

export default class Dashboard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            nodes: ['qr'],
            msgs: []
        }
    }
    componentDidMount() {
        const socket = this.props.socket;
        socket.on('testchannel', (data) => {
            this.parse_data(data.split('\n'))
        })
        this.scrollToBottom();
    }

    parse_data(d) {
        d.forEach(element => {
            if (element === '') {
                return;
            }
            if (element.includes("Node registered")) {
                let nodeType = element.split(': ')[1]
                console.log("REGISTERED " + nodeType)
                this.setState(prevState => ({
                    nodes: [...prevState.nodes, nodeType],
                    msgs: [...prevState.msgs, 'REGISTERED NEW NODE TYPE: ' + nodeType]
                }))
                return;
            }
            if (element.includes("has submitted")) {
                let usr = element.split(' ')[0];
                console.log(element.split(' ')[0] + '')
                this.setState(prevState => ({
                    msgs: [...prevState.msgs, usr + ' SUBMITTED A SHARE']
                }))
                return;
            }
            if (element.includes("is Authorized")) {
                var who = element.substring(
                    element.indexOf("(") + 1,
                    element.indexOf(")")
                );
                console.log(who + ' AUTHORIZED');
                this.setState(prevState => ({
                    msgs: [...prevState.msgs, who + ' HAS BEEN AUTHORIZED']
                }))
                return;
            }
            if (element === 'Looking for updates') {
                console.log('LOOKING')
                this.setState(prevState => ({
                    msgs: [...prevState.msgs, 'LOOKING FOR UPDATES']
                }))
                return;
            }
            if (element === 'Sending New Share to other Auth Nodes') {
                console.log("UPDATING OTHER AUTHS")
                this.setState(prevState => ({
                    msgs: [...prevState.msgs, "UPDATING OTHER AUTHS"]
                }))
            }
            if (element === 'Recieved Share from Client Node') {
                console.log("RECEIVED")
                this.setState(prevState => ({
                    msgs: [...prevState.msgs, "RECEIVED SHARE FROM A CLIENT"]
                }))
                return;
            }
            if (element === 'Sending Update to Client Node') {
                console.log("SENDING UPDATES")
                this.setState(prevState => ({
                    msgs: [...prevState.msgs, "SENDING UPTDATE TO CLIENT NODES"]
                }))
                return;
            }
            if (element === "Got Share") {
                console.log("RECEIVED2")
                this.setState(prevState => ({
                    msgs: [...prevState.msgs, "ALTERNATIVE SHARE RECEIVED"]
                }))
                return
            }
            console.log('FELL THROUGH: ' + element)
        });
    }

    componentDidUpdate() {
        this.scrollToBottom();
    }

    scrollToBottom() {
        this.el.scrollIntoView({ behavior: 'smooth' });
    }


    render() {
        return <div>
            <h3 className="section_heading">Nodes Online</h3>
            <RenderMap active={this.state.nodes} />
            <br></br>
            <h3 className="section_heading" >Output Log</h3>
            <Container fluid style={{ width: "95%" }}>
                <div className="log overflow-auto">
                    {this.state.msgs && this.state.msgs.map(item => <p>{item}</p>)}
                    <div ref={el => { this.el = el; }} />
                </div>
            </Container>
        </div>
    }
}

function RenderLog(props) {
}

function RenderMap(props) {
    return <Container fluid style={{ width: "95%" }}>
        <Row>
            <RenderIcon icon={<GiLockedFortress />} label={'Auth Node'} />
        </Row>
        <Row>
            {props.active.includes('face') &&
                <RenderIcon icon={<GiCyborgFace />} label={'Face ID'} />}

            {props.active.includes('web') &&
                <RenderIcon icon={<FaGlobe />} label={'Web ID'} />}

            {props.active.includes('other') &&
                <RenderIcon icon={<FaServer />} label={'Unknown Node'} />}

            {props.active.includes('voice') &&
                <RenderIcon icon={<GiSpeaker />} label={'Speech ID'} />}

            {props.active.includes('qr') &&
                <RenderIcon icon={<FaBarcode />} label={'QR Scan ID'} />}
        </Row>
    </Container>

}

function RenderIcon(props) {
    return <IconContext.Provider value={{ size: '5em' }}>
        <Col>
            {props.icon}
            <h3>{props.label}</h3>
        </Col>
    </IconContext.Provider>
}