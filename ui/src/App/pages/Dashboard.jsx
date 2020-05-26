/* eslint-disable react/no-array-index-key */
import React from 'react';
import {
  Container, Row, Col, Button,
} from 'react-bootstrap';
import { GiSpeaker, GiCyborgFace, GiLockedFortress } from 'react-icons/gi';
import {
  FaBarcode, FaGlobe, FaServer, FaArrowCircleRight,
} from 'react-icons/fa';
import { IconContext } from 'react-icons';
import PropTypes from 'prop-types';
import Modal from 'simple-react-modal';

import './Dashboard.css';

export default class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: [],
      msgs: [],
      usrs: [],
      numAuthNodes: 0,
      numOtherNodes: 0,
      show: false,
    };

    this.initiateRegister = this.initiateRegister.bind(this);
  }

  // Listen for new data coming in on testchannel
  // parse it for useful information
  componentDidMount() {
    const { socket, savedState } = this.props;
    if (savedState !== null) {
      this.setState(savedState);
    }
    socket.emit('DashboardUpdate')
    socket.on('DashboardUpdate', (data) => {
        console.log(data);
        this.parseData(data);
    });
    this.scrollToBottom();
  }

  // When state updates, smooth scroll the output log to its bottom
  componentDidUpdate() {
    this.scrollToBottom();
  }

  // when other screens are visited,
  // persist the state of the dashboard
  componentWillUnmount() {
    const { liftState } = this.props;
    liftState(this.state);
  }

  // show the registration modal
  show = () => {
    this.setState({ show: true });
  }

  // hide the registration modal
  hide = () => {
    this.setState({ show: false });
  }

  // Retrieve useful information from the multicast message
  parseData(d) {
    this.setState((prevState) => ({
        msgs: [...prevState.msgs, `${d.action}`],
    }));
      if (d.clients){ 
        let clientNodeCount = 0;
        d.clients.map((client) => {
            if (client.database === 'auth'){
                this.setState({
                    numAuthNodes: client.number
                })
            } else {
                clientNodeCount += 1;
            }
        })
        this.setState({
            nodes: d.clients,
            numOtherNodes: clientNodeCount
        })
      }
      if (d.users){ 
        this.setState({
            usrs: d.users,
        })
      }
  }


  // smooth scroll to bottom to keep new messages in focus
  scrollToBottom() {
    this.el.scrollIntoView({ behavior: 'smooth' });
  }

  // Check if username and fullname are both supplied
  // before initiating the register script on the backend
  initiateRegister() {
    const { registerHandler } = this.props;
    const username = document.getElementById('username').value;
    const fullname = document.getElementById('fullname').value;
    if (username === '' || fullname === '') {
      document.getElementById('send-arrow').style.color = 'red';
    } else {
      registerHandler(username, fullname);
    }
  }

  render() {
    const { state } = this;
    const {
      show, nodes, msgs, usrs, numAuthNodes, numOtherNodes
    } = state;
    const { threshold, total } = this.props;
    return (
      <div style={{ height: '100%' }}>
        <Button className="register-btn" variant="dark" onClick={this.show}>
          Register a new user
        </Button>
        <Modal
          className="username-modal" // this will completely overwrite the default css
          containerClassName="modal-container"
          closeOnOuterClick
          show={show}
          onClose={this.hide}
        >
          <h3 className="modal-title">Register a New User</h3>
          <div className="modal-background">
            <div className="input-boxes">
              <input id="username" placeholder="username" />
              <input id="fullname" placeholder="fullname" />
            </div>
            <div id="send-arrow" className="icon-holder">
              <FaArrowCircleRight className="clickable" onClick={this.initiateRegister} size={32} />
            </div>
          </div>

        </Modal>
        <h3 className="section_heading">Nodes Online</h3>
        <RenderMap active={nodes} threshold={threshold} numAuthNodes={numAuthNodes} numOtherNodes={numOtherNodes}/>
        <br />

        <Container fluid style={{ height: '40%', width: '95%' }}>
          <Row style={{ height: '5%', width: 'auto' }}>
            <h3 className="section_heading" style={{ width: '45%', marginLeft: '0px' }}>Output Log</h3>
            <h3 className="section_heading" style={{ width: '45%' }}>Current Users</h3>
          </Row>
          <Row style={{ height: '90%', width: 'auto' }}>
            <div className="col log overflow-auto">
              {msgs && msgs.map((item, i) => <p key={i}>{item}</p>)}
              <div ref={(el) => { this.el = el; }} />
            </div>
            <div className="col" style={{ margin: '0px' }}>
              <Container fluid style={{ height: '100%', width: '100%', borderStyle: 'none' }}>
                <Row style={{ height: '100%', width: 'auto' }}>
                  {usrs && usrs.map((usr, i) => (
                    <ShareCounter
                      key={i}
                      usr={usr.user}
                      num={usr.num_shares}
                      threshold={threshold}
                      total={total}
                    />
                  ))}
                </Row>
              </Container>
            </div>
          </Row>
        </Container>
        <br />
      </div>
    );
  }
}

// this function creates a bar indicater to show how many
// shares a user has submitted
// it takes the following as props:
// total - total number of shares
// threshold - threshold value for registration
// num - number of shares designated user has
// usr - the username to display
function ShareCounter(props) {
  const {
    total, num, usr, threshold,
  } = props;
  return (
    <Col>
      <Container>
        {
          (total - num > 0)
            && Array(total - num).fill(' ').map((_, i) => <Row key={i} className="empty" style={{ height: '50px', width: '50px', margin: '0 auto 0 auto' }} />)
}
        {Array(Math.min(total, num)).fill(' ').map((_, i) => <Row key={i} className={num >= threshold ? 'authorized' : 'unauthorized'} style={{ height: '50px', width: '50px', margin: '0 auto 0 auto' }} />)}
      </Container>
      <p>
        {usr}
        {' '}
        (
        {num}
        /
        {threshold}
        )
      </p>
    </Col>
  );
}

// this function takes care of displaying whichever nodes are
// currently in state (the nodes that have been registered to the backend)
function RenderMap(props) {
  return (
    <Container fluid className={props.numOtherNodes < props.threshold ? 'unauthorized' : ''} style={{ width: '95%' }}>
      <Row style={{ width: 'auto' }}>
        <RenderIcon icon={<GiLockedFortress />} label="Auth Node" number={props.numAuthNodes}/>
      </Row>
      <Row style={{ width: 'auto' }}>
        {props.active && props.active.map((nodeType, i) => {
          switch (nodeType.database) {
            case 'face':
              return <RenderIcon key={i} icon={<GiCyborgFace />} label="Face ID" number={nodeType.number} />;
            case 'web':
              return <RenderIcon key={i} icon={<FaGlobe />} label="Web ID" number={nodeType.number} />;
            case 'other':
              return <RenderIcon key={i} icon={<FaServer />} label="Unknown Node" number={nodeType.number}  />;
            case 'voice':
              return <RenderIcon key={i} icon={<GiSpeaker />} label="Speech ID" number={nodeType.number} />;
            case 'qr':
              return <RenderIcon key={i} icon={<FaBarcode />} label="QR Scan ID" number={nodeType.number} />;
          }
        })}
      </Row>
    </Container>
  );
}

function RenderIcon(props) {
  return (
    <IconContext.Provider value={{ size: '5em' }}>
      <Col>
        {props.icon}
        <h3>{props.label} (x{props.number})</h3>
      </Col>
    </IconContext.Provider>
  );
}

Dashboard.defaultProps = null;

Dashboard.propTypes = {
  liftState: PropTypes.func.isRequired,
  socket: PropTypes.shape({}).isRequired,
  savedState: PropTypes.shape({}),
  registerHandler: PropTypes.func.isRequired,
  threshold: PropTypes.number.isRequired,
  total: PropTypes.number.isRequired,
};
