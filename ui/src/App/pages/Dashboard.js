import React from 'react'
import { Container, Row, Col } from 'react-bootstrap'
import { GiSpeaker, GiCyborgFace, GiLockedFortress } from 'react-icons/gi'
import { FaBarcode, FaGlobe, FaServer } from 'react-icons/fa'
import { IconContext } from "react-icons";

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
            nodes: [],
            msgs: [],
            usrs: []
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
                let nodeType = element.split(': ')[1].trim()
                console.log("REGISTERED " + nodeType)
                this.setState(prevState => ({
                    nodes: [...prevState.nodes, nodeType],
                    msgs: [...prevState.msgs, 'REGISTERED NEW NODE TYPE: ' + nodeType]
                }))
                return;
            }
            if (element.includes("has submitted")) {
                let usr = element.split(' ')[0].trim();


                if (this.state[usr]){
                    this.setState(prevState => ({
                        msgs: [...prevState.msgs, usr + ' SUBMITTED A SHARE'],
                        [usr]: prevState[usr] + 1,
                    }))
                }
                else {
                    this.setState(prevState => ({
                        msgs: [...prevState.msgs, usr + ' SUBMITTED A SHARE'],
                        usrs: [...prevState.usrs, usr],
                        [usr]: 1
                    }))
                }

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
            this.setState(prevState => ({
                msgs: [...prevState.msgs, "MESSAGE: " + element]
            }))
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
        return <div style={{ height: "100%"}}>
            <h3 className="section_heading">Nodes Online</h3>
            <RenderMap active={this.state.nodes} threshold={this.props.threshold} />
            <br></br>

            <Container fluid style={{ height: '40%', width: "95%" }}>
                <Row style={{ height: '5%', width: 'auto' }}>
                    <h3 className="section_heading" style={{width: '45%', marginLeft: '0px'}} >Output Log</h3>
                    <h3 className="section_heading" style={{width: '45%'}} >Current Users</h3>
                </Row>
                <Row style={{ height: '90%', width: 'auto' }}>
                    <div className="col log overflow-auto">
                        {this.state.msgs && this.state.msgs.map((item, i) => <p key={i}>{item}</p>)}
                        <div ref={el => { this.el = el; }} />
                    </div>
                    <div className="col" style={{margin: '0px'}}>
                        <Container fluid style={{ height: '100%', width: "100%", borderStyle: 'none' }}>
                            <Row style={{ height: '100%', width: 'auto' }}>
                                {this.state.usrs &&
                                    this.state.usrs.map((usr, i) =>
                                        <ShareCounter key={i} usr={usr} num={this.state[usr]} threshold={this.props.threshold} total={this.props.total} />)}
                            </Row>
                        </Container>
                    </div>
                </Row>
            </Container>
            <br></br>
        </div>
    }
}

function ShareCounter(props) {
    return <Col>
    <Container>
        {
          (props.total - props.num > 0) &&
            Array(props.total - props.num).fill(' ').map((_, i) => {
            return <Row key={i} className='empty' style={{ height: '50px', width: '50px', margin: '0 auto 0 auto'}}></Row>
        })}
        {Array(Math.min(props.total, props.num)).fill(' ').map((_, i) => {
            return <Row key={i} className={props.num >= props.threshold ? 'authorized' : 'unauthorized'} style={{ height: '50px', width: '50px', margin: '0 auto 0 auto'}}></Row>
        })}
    </Container>
        <p>{props.usr} ({props.num}/{props.threshold})</p>
    </Col>
}

function RenderMap(props) {
    return <Container fluid className={props.active.length < props.threshold ? 'unauthorized' : ''} style={{ width: "95%" }}>
        <Row style={{width: 'auto'}}>
            <RenderIcon icon={<GiLockedFortress />} label={'Auth Node'} />
        </Row>
        <Row style={{width: 'auto'}}>
            {props.active && props.active.map((nodeType, i) => {
                switch(nodeType){
                    case 'face':
                        return <RenderIcon key={i} icon={<GiCyborgFace />} label={'Face ID'} />
                    case 'web':
                        return <RenderIcon key={i} icon={<FaGlobe />} label={'Web ID'} />
                    case 'other':
                        return <RenderIcon key={i} icon={<FaServer />} label={'Unknown Node'} />
                    case 'voice':
                        return <RenderIcon key={i} icon={<GiSpeaker />} label={'Speech ID'} />
                    case 'qr':
                        return <RenderIcon key={i} icon={<FaBarcode />} label={'QR Scan ID'} />
                }
            })}
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