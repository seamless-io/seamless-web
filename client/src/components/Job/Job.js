import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

import { Row, Col } from 'react-bootstrap';

import { getJob } from '../../api';

import './style.css';
import download from '../../images/cloud-download.svg';

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
    </>
  );
};

export default Job;
