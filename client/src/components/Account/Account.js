import React, { useState, useEffect } from 'react';

import { Row, Col, Spinner } from 'react-bootstrap';
import { AiOutlineMail, AiOutlineApi } from 'react-icons/ai';
import { loadStripe } from '@stripe/stripe-js';

import { getUserInfo, createStripeCheckoutSession } from '../../api';
import Notification from '../Notification/Notification';

import './style.css';

const stripePromise = loadStripe('pk_test_51HNZJpJgB05uRN01mxmJDdn7yjEdR2RONjc8SGYbHsip7CuHd2alN6ufPrJPK1qBipDk7Dm4CFle5w5eSke7sxrQ003bQiBndI');

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

  const checkout = async (event) => {
    setLoading(true);
    createStripeCheckoutSession()
      .then(payload => {
        stripePromise.then(stripe => {
            console.log({'sessionId': payload['session_id']});
            stripe.redirectToCheckout({'sessionId': payload['session_id']});
            // If `redirectToCheckout` fails due to a browser or network
            // error, display the localized error message to your customer
            // using `error.message`.
        })
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to create checkout session',
          'danger'
        );
      });
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
      <div className="smls-card">
      <button
          type="button"
          onClick={checkout}
        >
        <span> Update Billing Info </span>
      </button>
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
