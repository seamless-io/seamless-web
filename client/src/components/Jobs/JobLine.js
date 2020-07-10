import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

import { Row, Col, Button, Badge } from 'react-bootstrap';

import { triggerJobRun } from '../../api';

import play from '../../images/play-filled.svg';

const JobLine = ({ name, schedule, status, id }) => {
  const history = useHistory();
  const [scheduleValue, setScheduleValue] = useState(schedule);
  const [scheduleClassName, setScheduleClassName] = useState('');
  const openJob = () => {
    history.push(`jobs/${id}`);
  };

  if (scheduleValue === 'None') {
    setScheduleValue('Not scheduled');
    setScheduleClassName('smls-muted');
  }

  const jobRunButton = jobId => {
    return (
      <button
        onClick={() => triggerJobRun(jobId)}
        className="smls-job-line-run-button"
      >
        <img src={play} className="smls-job-play" alt="Job run" />
        <span className="smls-job-line-run-button-text">Run Now</span>
      </button>
    );
  };

  return (
    <Row className="smls-job-line">
      <Col sm={4} onClick={openJob} className="smls-job-line-name-container">
        <span className="smls-job-name">{name}</span>
      </Col>
      <Col sm={4}>
        <span className={`smls-job-schedule ${scheduleClassName}`}>
          {scheduleValue}
        </span>
      </Col>
      <Col sm={2}>
        <Badge
          className={`smls-job-status smls-status-${status.toLowerCase()}`}
        >
          {status}
        </Badge>
      </Col>
      <Col sm={2}>{jobRunButton(id)}</Col>
    </Row>
  );
};

export default JobLine;
