import React from 'react';

import { Navbar, Nav, Row, Col } from 'react-bootstrap';

import './style.css';
import logo from '../../images/seamless-logo-black.svg';
import logout from '../../images/circle-arrow-right.svg';
import userAccount from '../../images/user.svg';
import jobsLogo from '../../images/lightning.svg';

const ApplicationHeader = () => {
  return (
    <Navbar expand="lg" className="smls-header">
      <Row className="smls-header">
        <Col>
          <Navbar.Brand href="#home">
            <img src={logo} className="smls-logo" alt="SeamlessCloud logo" />
          </Navbar.Brand>
        </Col>
        <Col className="smls-header-center">
          <Nav.Link href="/">
            <img src={jobsLogo} className="smls-jobs" alt="Jobs" />
            Jobs
          </Nav.Link>
          <Nav.Link href="/account">
            <img src={userAccount} className="smls-user" alt="User account" />
            My Account
          </Nav.Link>
        </Col>
        <Col className="smls-header-logout">
          <Nav.Link
            href={window.location.origin + '/logout'}
            className="smls-header-right"
          >
            <img src={logout} className="smls-logout" alt="Logout" />
            Logout
          </Nav.Link>
        </Col>
      </Row>
    </Navbar>
  );
};

export default ApplicationHeader;
