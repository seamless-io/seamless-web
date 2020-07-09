import React, { useState } from 'react';
import { Row, Col } from 'react-bootstrap';

import reset from '../../images/rotate-left.svg';
import copy from '../../images/copy.svg';
import key from '../../images/key.svg';
import './style.css';

const Account = () => {
  return (
    <div className="smls-account-container">
      <div className="smls-account-header">
        <Row>
          <Col>
            <h1 className="smls-account-header">My Account</h1>
          </Col>
        </Row>
      </div>
      <div className="smls-account-key smls-card">
        <Row>
          <Col sm={12}>
            <h5 className="smls-account-key-header">API Key</h5>
          </Col>
          <Col sm={7}>
            <div className="smls-account-key-text">
              <img src={key} className="smls-account-key" alt="Api key" />
              <span>sdjkn234jsdjfnsn923kjn3oisdkj</span>
            </div>
          </Col>
          <Col sm={2}>
            <div className="smls-account-copy-container">
              <button className="smls-account-copy-button">
                <img src={copy} className="smls-account-copy" alt="Copy" />
                <span className="smls-account-copy-button-text">Copy</span>
              </button>
            </div>
          </Col>
          <Col sm={3}>
            <div className="smls-account-reset-key-container">
              <button className="smls-account-reset-key-button">
                <img
                  src={reset}
                  className="smls-account-reset"
                  alt="Reset key"
                />
                <span className="smls-account-reset-button-text">
                  Reset Key
                </span>
              </button>
            </div>
          </Col>
        </Row>
      </div>
      <div className="smls-account-email smls-card">
        <Row>
          <Col sm={12}>
            <h5 className="smls-account-key-header">My Email</h5>
          </Col>
          <Col sm={12}>test.testovich@test.test</Col>
        </Row>
      </div>
      <div className="smls-account-password smls-card">
        <Row>
          <Col sm={12}>
            <h5 className="smls-account-key-header">Change Password</h5>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Account;
