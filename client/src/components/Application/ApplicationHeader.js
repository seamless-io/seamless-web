import React from 'react';

import {
  Navbar,
  Nav,
  Row,
  Col,
  OverlayTrigger,
  Popover,
} from 'react-bootstrap';
import {
  AiOutlineFileAdd,
  AiOutlineUser,
  AiOutlineThunderbolt,
  AiOutlineLogout,
  AiOutlineInfoCircle,
} from 'react-icons/ai';

import './style.css';
import logo from '../../images/seamless-logo-black.svg';

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
              <AiOutlineThunderbolt
                size={18}
                style={
                  location.pathname === '/'
                    ? { color: '#016bff', marginRight: '5px' }
                    : { color: '#1a1a1a', marginRight: '5px' }
                }
              />
              Jobs
            </Nav.Link>
          </div>
          <div
            className={`smls-header-jobs-container ${
              location.pathname === '/templates' ? 'smls-header-active' : ''
            }`}
          >
            <Nav.Link href="/templates" className="smls-header-link">
              <AiOutlineFileAdd
                size={18}
                style={
                  location.pathname === '/templates'
                    ? { color: '#016bff', marginRight: '5px' }
                    : { color: '#1a1a1a', marginRight: '5px' }
                }
              />
              Templates
            </Nav.Link>
          </div>
          <div
            className={`smls-header-jobs-container ${
              location.pathname === '/account' ? 'smls-header-active' : ''
            }`}
          >
            <Nav.Link href="/account" className="smls-header-link">
              <AiOutlineUser
                size={18}
                style={
                  location.pathname === '/account'
                    ? { color: '#016bff', marginRight: '5px' }
                    : { color: '#1a1a1a', marginRight: '5px' }
                }
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
              <AiOutlineLogout size={18} style={{ marginRight: '5px' }} />
              Logout
            </Nav.Link>
            <div className="smls-header-right smls-header-information nav-link">
              <OverlayTrigger
                trigger="click"
                placement="bottom"
                rootClose={true}
                overlay={
                  <Popover>
                    <Popover.Content>
                      <a href="/faq/cli">What is smls CLI tool? How do I use it?</a>
                    </Popover.Content>
                    <Popover.Content>
                      <a href="/faq/templates">What are Templates?</a>
                    </Popover.Content>
                    <Popover.Content>
                      Support: hello@seamlesscloud.io
                    </Popover.Content>
                  </Popover>
                }
              >
              <div>
                <AiOutlineInfoCircle
                  size={18}
                  style={{ marginRight: '5px', cursor: 'pointer' }}
                >
                </AiOutlineInfoCircle>
                <span className="smls-header-link">FAQ</span>
                </div>
              </OverlayTrigger>
            </div>
          </div>
        </Col>
      </Row>
    </Navbar>
  );
};

export default ApplicationHeader;
