import React, { useState, useEffect } from 'react';
import { Row, Col, Spinner } from 'react-bootstrap';

import { getUserInfo } from '../../api';

import './style.css';

const JobTemplates = () => {
  return (
    <div className="smls-account-container">
      <div className="smls-account-header-container">
        <Row>
          <Col>
            <h1 className="smls-account-header">Job Templates</h1>
          </Col>
        </Row>
      </div>
      <div className="smls-card">
        <Row>
          <Col sm={12}>
            <div className="smls-guide-requiremets">
              <p>
                Job Templates are examples of Jobs that are available for you to add to your account. You can find them if you go to the "Templates" tab.
              </p>
              <p>
                Each template in our Library showcases a unique use case of Seamless Jobs. Templates contain code that integrates with popular 3rd party services and tools. Each template has instructions on how to use it (including instructions on how to set up 3rd party tools).
              </p>
              <p>
                After you've created a Job out of the template - you're free to do any changes. You can set up your own Job Parameters or change the code. If you want to change the code - our Command Line Interface tool called <code>smls</code> will be useful. You can read more about it <a href="/faq/cli">here</a>.
              </p>
              <p>
                If you have any questions don't hesitate to email us at
                <strong> hello@seamlesscloud.io</strong>.
              </p>
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default JobTemplates;
