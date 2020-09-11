import React, { useState, useEffect } from 'react';
import { Row, Col, Spinner } from 'react-bootstrap';

import { getUserInfo } from '../../api';

import './style.css';

const Guide = () => {
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(null);

  useEffect(() => {
    setLoading(true);
    getUserInfo()
      .then(payload => {
        setApiKey(payload.api_key);
        setLoading(false);
      })
      .catch(() => {
        alert('Error!'); // TODO: create a notification component
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
            <h1 className="smls-account-header">Quick Start Guide</h1>
          </Col>
        </Row>
      </div>
      <div className="smls-card">
        <Row>
          <Col sm={12}>
            <div className="smls-guide-requiremets">
              <p>
                <code>smls</code> client requires Python 3.6 or higher and pip
                installed.
              </p>
              <p>
                If you have any questions don't hesitate to email us at
                <strong> hello@seamlesscloud.io</strong>.
              </p>
            </div>
          </Col>
          <Col sm={12}>
            <div className="smls-guide-code-section">
              <code className="smls-code-comment"># install smls library</code>
              <code>pip install smls</code>
              <br />
              <code className="smls-code-comment"># check smls version</code>
              <code>pip list | grep smls</code>
              <br />
              <code className="smls-code-comment">
                # authenticate smls client
              </code>
              <code>{`smls auth ${apiKey}`}</code>
              <br />
              <code className="smls-code-comment"># create an example job</code>
              <code>smls example</code>
              <br />
              <code className="smls-code-comment">
                # go into the folder with the example job
              </code>
              <code>cd stock_monitoring_job</code>
              <br />
              <code className="smls-code-comment">
                # deploy and schedule the job every day at 00:00 UTC
              </code>
              <code>
                smls publish --name "Stock Price Monitoring" --schedule "0 0 * *
                *"
              </code>
              <br />
              <code className="smls-code-comment"># remove the job</code>
              <code>smls remove --name "Stock Price Monitoring"</code>
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Guide;
