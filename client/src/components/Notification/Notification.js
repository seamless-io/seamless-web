import React, { useState } from 'react';

import { Toast } from 'react-bootstrap';

import './style.css';
import success from '../../images/notification_success.svg';

const Notification = ({ show, closeNotification }) => {
  console.log(show);
  return (
    <Toast
      onClose={closeNotification}
      delay={3000}
      show={show}
      autohide={true}
      className="smls-toast-notificaiton"
    >
      <Toast.Header>
        <img src="holder.js/20x20?text=%20" className="rounded mr-2" alt="" />
        <img src={success} className="rounded mr-2" alt="notification" />
        <strong className="mr-auto">My custom notification</strong>
      </Toast.Header>
    </Toast>
  );
};

export default Notification;
