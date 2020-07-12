import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

import { Row, Col } from 'react-bootstrap';

import { getJob } from '../../api';

import './style.css';
import download from '../../images/cloud-download.svg';
import timeHistory from '../../images/time-history.svg';
import pencil from '../../images/pencil-create.svg';

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
          <div className="smls-job-heade-container">
            <h1 className="smls-job-name-h1">{name}</h1>
            <button
              className="smls-job-name-pencil"
              onClick={() => alert('Not working yet.')}
            >
              <img src={pencil} alt="Updated at" />
            </button>
          </div>
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
            <span>Scheduled for every Monday, at 12 PM</span>
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
              <div className="smls-job-info-section-col">
                <h5>Execution Timeline</h5>
              </div>
            </Col>
          </Row>
          <Row>
            <Col>
              <div className="smls-job-info-section-col-scheduled">
                <div className="smls-job-info-section-col-scheduled-text">
                  Devember 25, 2020, 05:08
                </div>
                <div className="smls-job-info-section-col-scheduled-badge">
                  <span>scheduled</span>
                </div>
              </div>
            </Col>
          </Row>
          <Row>
            <Col>
              <div className="smls-job-info-section-col-hr">
                <hr />
              </div>
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
