import React from 'react';

import {
  Navbar,
  Nav,
  Row,
  Col,
  OverlayTrigger,
  Popover,
} from 'react-bootstrap';

import './style.css';
import logo from '../../images/seamless-logo-black.svg';
import logout from '../../images/circle-arrow-right.svg';
import userAccount from '../../images/user.svg';
import userAccountInactive from '../../images/user-inactive.svg';
import jobsLogo from '../../images/lightning.svg';
import jobsLogoInactive from '../../images/lightning-inactive.svg';
import information from '../../images/information.svg';

const ApplicationHeader = () => {
  return (
    <Navbar expand="lg" className="smls-header">
      <Row className="smls-header">
        <Col>
          <Navbar.Brand href="/">
            <img src={logo} className="smls-logo" alt="SeamlessCloud logo" />
          </Navbar.Brand>
        </Col>
        <Col className="smls-header-center">
          <div
            className={`smls-header-jobs-container ${
              location.pathname === '/' ? 'smls-header-active' : ''
            }`}
          >
            <Nav.Link href="/" className="smls-header-link">
              <img
                src={location.pathname === '/' ? jobsLogo : jobsLogoInactive}
                className="smls-jobs"
                alt="Jobs"
              />
              Jobs
            </Nav.Link>
          </div>
          <div
            className={`smls-header-jobs-container ${
              location.pathname === '/account' ? 'smls-header-active' : ''
            }`}
          >
            <Nav.Link href="/account" className="smls-header-link">
              <img
                src={
                  location.pathname === '/account'
                    ? userAccount
                    : userAccountInactive
                }
                className="smls-user"
                alt="User account"
              />
              My Account
            </Nav.Link>
          </div>
        </Col>
        <Col className="smls-header-logout">
          <div style={{ width: '100%' }}>
            <Nav.Link
              href={`${window.location.origin}/logout`}
              className="smls-header-right smls-header-link"
            >
              <img src={logout} className="smls-logout" alt="Logout" />
              Logout
            </Nav.Link>
            <div className="smls-header-right smls-header-information nav-link">
              <OverlayTrigger
                trigger="click"
                placement="bottom"
                overlay={
                  <Popover>
                    <Popover.Content>
                      <strong>Contact support:</strong> hello@seamlesscloud.io
                    </Popover.Content>
                  </Popover>
                }
              >
                <img
                  src={information}
                  className="smls-information"
                  alt="Information"
                />
              </OverlayTrigger>
            </div>
          </div>
        </Col>
      </Row>
    </Navbar>
  );
};

export default ApplicationHeader;
