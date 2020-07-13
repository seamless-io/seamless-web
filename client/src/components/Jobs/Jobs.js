import React, { useState, useEffect } from 'react';
import openSocket from 'socket.io-client';
import { Row, Col } from 'react-bootstrap';

import { getJobs, updateJob } from '../../api';
import JobLine from './JobLine';

import './style.css';

import linkExternal from '../../images/link-external.svg';
import jobsLogo from '../../images/lightning.svg';
import terminal from '../../images/terminal.svg';

const Jobs = () => {
  const [jobs, setjobs] = useState([]);
  const [noJobsStyle, setNoJobsStyle] = useState('');

  useEffect(() => {
    getJobs()
      .then(payload => {
        setjobs(payload);
        setNoJobsStyle(
          payload && payload.length > 0 ? '' : 'smls-no-jobs-header'
        );
      })
      .catch(() => {
        alert('Error!');
      });
  }, []);

  const renderJobs = () => {
    if (jobs && jobs.length > 0) {
      return (
        <>
          <Row className="smls-jobs-column-names">
            <Col sm={4}>NAME</Col>
            <Col sm={4}>SCHEDULE</Col>
            <Col sm={2}>STATUS</Col>
            <Col sm={2}>CONTROLS</Col>
          </Row>
          {jobs.map(job => (
            <JobLine key={job.id} {...job} />
          ))}
        </>
      );
    }

    return (
      <>
        <Row className="smls-no-jobs">
          <Col className="smls-no-jobs-icon-container">
            <div className="smls-no-jobs-icon blue">
              <img src={jobsLogo} className="smls-jobs" alt="Jobs"></img>
            </div>
            <div className="smls-no-jobs-message">
              <div>
                <strong>You have no jobs</strong>
              </div>
              <div>
                To proceed with seamless - install & configure seamless CLI.
              </div>
            </div>
          </Col>
        </Row>
        <Row className="smls-no-jobs">
          <Col className="smls-no-jobs-icon-container">
            <div className="smls-no-jobs-icon green">
              <img src={terminal} className="smls-jobs" alt="Terminal"></img>
            </div>
            <div className="smls-no-jobs-message">
              <p>
                Installation Guide<sup>*</sup>
              </p>
              <p>
                Copy this into your terminal, run the command, and follow
                further instractions:
              </p>
              <p>pip install seamless-cli</p>
              <p>* Requires Python 3.6 or higher</p>
            </div>
          </Col>
        </Row>
      </>
    );
  };

  return (
    <>
      <Row className={`smls-jobs-header ${noJobsStyle}`}>
        <Col className="smls-my-jobs-header">
          <h1 className="smls-my-jobs-h1">My Jobs</h1>
        </Col>
        <Col className="smls-jobs-header-buttons-container">
          <div className="smls-jobs-header-buttons">
            <button
              className="smls-button-add-jobs"
              onClick={() => alert('Not working yet.')}
            >
              <img src={linkExternal} alt="External link" />
              <span className="smls-jobs-leaen-add-jobs-text">
                Learn how to create jobs
              </span>
            </button>
          </div>
        </Col>
      </Row>
      {renderJobs()}
    </>
  );
};

export default Jobs;
