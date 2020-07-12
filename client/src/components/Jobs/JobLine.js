import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

import { Row, Col, Badge, OverlayTrigger, Tooltip } from 'react-bootstrap';
import Toggle from 'react-toggle';

import { triggerJobRun } from '../../api';

import './toggle.css';
import play from '../../images/play-filled.svg';

const JobLine = ({ name, schedule, status, id }) => {
  const history = useHistory();
  const [scheduleValue, setScheduleValue] = useState(schedule);
  const [scheduleClassName, setScheduleClassName] = useState('');
  const [isScheduleOn, setIsScheduleOn] = useState(false);

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
        <span className="smls-job-line-name">{name}</span>
      </Col>
      <Col sm={4}>
        <OverlayTrigger
          key={id}
          placement="top"
          overlay={
            <Tooltip id={`tooltip-${id}`} className="smls-job-line-tooltip">
              Needs to be triggered manually.
            </Tooltip>
          }
        >
          <div className="smls-job-line-toggle-container">
            <Toggle
              defaultChecked={isScheduleOn}
              icons={false}
              onChange={() => alert('Not working yet.')}
            />
            <span className={`smls-job-line-schedule ${scheduleClassName}`}>
              {scheduleValue}
            </span>
          </div>
        </OverlayTrigger>
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
