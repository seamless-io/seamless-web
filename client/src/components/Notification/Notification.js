import React from 'react';
import PropTypes from 'prop-types';

import { Toast, Row, Col } from 'react-bootstrap';

import './style.css';
import success from '../../images/notification_success.svg';
import info from '../../images/notification_info.svg';
import warning from '../../images/notification_warning.svg';
import danger from '../../images/notification_danger.svg';
import close from '../../images/close.svg';

const Notification = ({ show, title, body, closeNotification, alertType }) => {
  let icon;
  if (alertType === 'success') {
    icon = success;
  } else if (alertType === 'info') {
    icon = info;
  } else if (alertType === 'warning') {
    icon = warning;
  } else {
    icon = danger;
  }
  return (
    <Toast
      onClose={closeNotification}
      delay={3000}
      show={show}
      autohide
      className="smls-toast-notificaiton"
    >
      <Toast.Body>
        <Row className="smls-notifcation-row">
          <Col sm={3}>
            <div className={`smls-notification-icon ${alertType}`}>
              <img src={icon} alt={`${icon} icon`} />
            </div>
          </Col>
          <Col sm={7}>
            <div className="smls-notification-title">{title}</div>
            <div className="smls-notification-body">{body}</div>
          </Col>
          <Col sm={2}>
            <div
              className="smls-notification-close"
              onClick={closeNotification}
            >
              <img src={close} alt="Close button" />
            </div>
          </Col>
        </Row>
      </Toast.Body>
    </Toast>
  );
};

export default Notification;

Notification.propTypes = {
  show: PropTypes.bool,
  title: PropTypes.string,
  body: PropTypes.string,
  closeNotification: PropTypes.func,
  alertType: PropTypes.string,
};

Notification.defaultProps = {
  show: false,
  title: '',
  body: '',
  closeNotification: null,
  alertType: '',
};
