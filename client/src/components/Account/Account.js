import React, { useState, useEffect } from 'react';
import { Row, Col } from 'react-bootstrap';

import { getUserInfo } from '../../api';

import reset from '../../images/rotate-left.svg';
import copy from '../../images/copy.svg';
import key from '../../images/key.svg';
import atSign from '../../images/at-sign.svg';
import './style.css';

const Account = () => {
  const [apiKey, setApiKey] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    getUserInfo()
      .then(payload => {
        setApiKey(payload.api_key);
        setEmail(payload.email);
      })
      .catch(() => {
        alert('Error!');
      });
  }, []);

  return (
    <div className="smls-account-container">
      <div className="smls-account-header-container">
        <Row>
          <Col>
            <h1 className="smls-account-header">My Account</h1>
          </Col>
        </Row>
      </div>
      <div className="smls-account-key smls-card">
        <Row>
          <Col sm={12} className="smls-account-section-header-container">
            <h5 className="smls-account-section-header">API Key</h5>
          </Col>
          <Col sm={7}>
            <div className="smls-account-key-text">
              <img src={key} className="smls-account-key" alt="Api key" />
              <span>{apiKey}</span>
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
          <Col sm={12} className="smls-account-section-header-container">
            <h5 className="smls-account-section-header">My Email</h5>
          </Col>
          <Col sm={7}>
            <div className="smls-account-key-text">
              <img src={atSign} className="smls-account-key" alt="Api key" />
              <span>{email}</span>
            </div>
          </Col>
        </Row>
      </div>
      <div className="smls-account-password smls-card">
        <Row>
          <Col sm={12} className="smls-account-section-header-container">
            <h5 className="smls-account-section-header">Change Password</h5>
          </Col>
          <Col sm={7} className="smls-account-input-contaier">
            <div>
              <label
                htmlFor="old-password"
                className="smls-account-input-label"
              >
                Old Password
              </label>
              <input className="smls-account-input" id="old-password"></input>
            </div>
          </Col>
          <Col sm={7} className="smls-account-input-contaier">
            <div>
              <label
                htmlFor="new-password"
                className="smls-account-input-label"
              >
                New Password
              </label>
              <input
                className="smls-account-input"
                id="new-password"
                placeholder="min. 8 characters"
              ></input>
            </div>
          </Col>
          <Col sm={7} className="smls-account-input-contaier">
            <div>
              <label
                htmlFor="confirm-password"
                className="smls-account-input-label"
              >
                Confirm New Password
              </label>
              <input
                className="smls-account-input"
                id="confrim-password"
              ></input>
            </div>
          </Col>
          <Col sm={7} className="smls-account-input-contaier">
            <div>
              <button className="smls-account-change-password-button">
                <span className="smls-account-change-password-button-text">
                  Change Password
                </span>
              </button>
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Account;
