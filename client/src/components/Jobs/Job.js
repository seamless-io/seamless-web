import React, { useState } from 'react';
import { Row, Col, Button, Badge } from 'react-bootstrap';

import { triggerJobRun } from '../../api';

import play from '../../images/play-filled.svg';

const Job = ({ name, schedule, status, id }) => {
  const [scheduleValue, setScheduleValue] = useState(schedule);
  const [scheduleClassName, setScheduleClassName] = useState('');
  const [statusClassName, setStatusClassName] = useState('new');

  if (scheduleValue === 'None') {
    setScheduleValue('Not scheduled');
    setScheduleClassName('smls-muted');
  }

  const jobRunButton = jobId => {
    return (
      <Button
        onClick={() => triggerJobRun(jobId)}
        className="smls-job-run-button"
      >
        <img src={play} className="smls-job-play" alt="Job run" />
        <span className="smls-job-run-button-text">Run Now</span>
      </Button>
    );
  };

  return (
    <Row className="smls-job">
      <Col sm={4}>
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

export default Job;
