import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

import { Row, Col } from 'react-bootstrap';

import { getJob } from '../../api';

import './style.css';
import download from '../../images/cloud-download.svg';
import timeHistory from '../../images/time-history.svg';

const Job = () => {
  const job = useParams();
  const [name, setName] = useState('');

  useEffect(() => {
    getJob(job.id)
      .then(payload => {
        setName(payload.name);
      })
      .catch(() => {
        alert('Error!');
      });
  }, []);

  return (
    <>
      <Row className="smls-job-header">
        <Col className="smls-job-name-header">
          <h1 className="smls-job-name-h1">{name}</h1>
        </Col>
        <Col className="smls-job-header-buttons-container">
          <div className="smls-job-header-buttons">
            <button className="smls-job-run-button">
              <span className="smls-job-run-button-text">Run</span>
            </button>
            <button className="smls-job-download-code-button">
              <img src={download} alt="Download code" />
              <span className="smls-job-download-code-button-text">
                Download Code
              </span>
            </button>
          </div>
        </Col>
      </Row>
      <Row className="smls-job-extra-info">
        <Col style={{ paddingLeft: '0px' }}>
          <div className="smls-job-extra-info-section">
            <span>Schedule</span>
          </div>
        </Col>
        <Col style={{ paddingRight: '0px' }}>
          <div className="smls-job-extra-info-section">
            <img src={timeHistory} alt="Updated at" />
            <span>Code updated on May 19, 2020, 14:56</span>
          </div>
        </Col>
      </Row>
      <Row className="smls-job-main-info">
        <Col
          sm={4}
          className="smls-job-main-info-section"
          style={{ borderRight: '2px solid #ebedf0' }}
        >
          <Row>
            <Col>
              <h5 className="smls-job-main-info-section-header">
                Execution Timeline
              </h5>
            </Col>
          </Row>
        </Col>
        <Col sm={8} className="smls-job-main-info-section">
          <Row>
            <Col sm={12}>
              <h5 className="smls-job-main-info-section-header">Logs</h5>
            </Col>
            <Col sm={12}>
              <div className="smls-job-container">logs....</div>
            </Col>
          </Row>
        </Col>
      </Row>
    </>
  );
};

export default Job;
