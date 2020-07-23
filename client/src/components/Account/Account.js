import React, { useState, useEffect } from 'react';
import { Row, Col, Spinner } from 'react-bootstrap';

import { getUserInfo } from '../../api';

import key from '../../images/key.svg';
import atSign from '../../images/at-sign.svg';
import './style.css';

const Account = () => {
  const [apiKey, setApiKey] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(null);

  useEffect(() => {
    setLoading(true);
    getUserInfo()
      .then(payload => {
        setApiKey(payload.api_key);
        setEmail(payload.email);
        setLoading(false);
      })
      .catch(() => {
        alert('Error!');
      });
  }, []);

  if (loading) {
    return (
      <div className="smls-jobs-spinner-container">
        <Spinner animation="border" role="status" />
      </div>
    );
  }

  return (
    <div className="smls-account-container">
      <div className="smls-account-header-container">
        <Row>
          <Col>
            <h1 className="smls-account-header">My Account</h1>
          </Col>
        </Row>
      </div>
      <div className="smls-card">
        <Row>
          <Col sm={12} className="smls-account-section-header-container">
            <h5 className="smls-account-section-header">API Key</h5>
          </Col>
          <Col sm={12}>
            <div className="smls-account-section-text">
              <img src={key} className="smls-account-key" alt="Api key" />
              <span>{apiKey}</span>
            </div>
          </Col>
        </Row>
      </div>
      <div className="smls-card">
        <Row>
          <Col sm={12} className="smls-account-section-header-container">
            <h5 className="smls-account-section-header">My Email</h5>
          </Col>
          <Col sm={12}>
            <div className="smls-account-section-text">
              <img src={atSign} className="smls-account-key" alt="Api key" />
              <span>{email}</span>
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Account;
