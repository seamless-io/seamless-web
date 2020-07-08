import React, { useState } from 'react';
import { Container, Row, Col, Button, Badge } from 'react-bootstrap';

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
          <Col sm={8}>Key</Col>
          <Col sm={2}>Copy</Col>
          <Col sm={2}>Refresh</Col>
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
