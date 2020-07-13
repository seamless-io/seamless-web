import React, { useState, useEffect } from 'react';
import openSocket from 'socket.io-client';
import { Row, Col } from 'react-bootstrap';

import { getJobs, updateJob } from '../../api';
import JobLine from './JobLine';

import './style.css';

import linkExternal from '../../images/link-external.svg';

const Jobs = () => {
  const [jobs, setjobs] = useState([]);
  const [noJobsStyle, setNoJobsStyle] = useState('');

  useEffect(() => {
    getJobs()
      .then(payload => {
        setjobs(payload);
        setNoJobsStyle(payload && payload.length > 0 ? '' : 'smls-no-jobs');
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
          <Col className="smls-no-jobs-message">
            <div>You have no jobs.</div>
            <div>
              To proceed with seamless - install & configure seamless CLI.
            </div>
          </Col>
        </Row>
        <Row></Row>
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
