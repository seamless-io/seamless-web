import React, { useState, useEffect } from 'react';

import { Row, Col, Spinner } from 'react-bootstrap';
import { AiOutlineMail, AiOutlineApi } from 'react-icons/ai';

import { getUserInfo } from '../../api';
import Notification from '../Notification/Notification';

import './style.css';

const Account = () => {
  const [apiKey, setApiKey] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(null);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');

  const displayNotification = (show, title, body, alterType) => {
    setShowNotification(show);
    setNotificationTitle(title);
    setNotificationBody(body);
    setNotificationAlertType(alterType);
  };

  const closeNotification = () => {
    setShowNotification(false);
  };

  useEffect(() => {
    setLoading(true);
    getUserInfo()
      .then(payload => {
        setApiKey(payload.api_key);
        setEmail(payload.email);
        setLoading(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to get the account info :(',
          'danger'
        );
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
              <AiOutlineApi size={20} style={{ color: '#9299a3' }} />
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
              <AiOutlineMail size={20} style={{ color: '#9299a3' }} />
              <span>{email}</span>
            </div>
          </Col>
        </Row>
      </div>
      <div className="smls-card">
        <Row>
          <Col sm={12} className="smls-account-section-header-container">
            <h5 className="smls-account-section-header">Contact Support</h5>
          </Col>
          <Col sm={12}>
            <div className="smls-account-section-text">
              <AiOutlineMail size={20} style={{ color: '#9299a3' }} />
              <span>hello@seamlesscloud.io</span>
            </div>
          </Col>
        </Row>
      </div>
      <Notification
        show={showNotification}
        closeNotification={closeNotification}
        title={notificationTitle}
        body={notificationBody}
        alertType={notificationAlertType}
      />
    </div>
  );
};

export default Account;
