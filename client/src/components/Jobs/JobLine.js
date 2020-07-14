import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';

import openSocket from 'socket.io-client';
import {
  Row,
  Col,
  Badge,
  OverlayTrigger,
  Tooltip,
  Toast,
} from 'react-bootstrap';
import Toggle from 'react-toggle';

import { triggerJobRun } from '../../api';

import './toggle.css';
import play from '../../images/play-filled.svg';

const JobLine = ({ name, schedule, status, id }) => {
  const history = useHistory();
  const [scheduleValue, setScheduleValue] = useState(schedule);
  const [statusValue, setStatusValue] = useState(status);
  const [scheduleClassName, setScheduleClassName] = useState('');
  const [isScheduleOn, setIsScheduleOn] = useState(false);
  const [isToggleDisabled, setIsToggleDisabled] = useState(true);
  const [isRunButtonDisabled, setIsRunButtonDisabled] = useState(false);
  const [showNotification, setShowNotification] = useState(true);

  if (scheduleValue === 'None') {
    setScheduleValue('Not scheduled');
    setScheduleClassName('smls-muted');
  }

  const socket = openSocket(
    location.protocol + '//' + document.domain + ':' + location.port + '/socket'
  );

  useEffect(() => {
    socket.on('status', data => updateJobStatus(data));
  }, []);

  const updateJobStatus = data => {
    setStatusValue(data.status);
    console.log(data);
    if (statusValue !== 'EXECUTING') {
      setIsRunButtonDisabled(false);
    }
  };

  const openJob = () => {
    history.push(`jobs/${id}`);
  };

  const runJob = () => {
    setIsRunButtonDisabled(true);
    setShowNotification(true);
    triggerJobRun(id)
      .then(payload => {
        setShowNotification(false);
      })
      .catch(payload => {
        console.log(payload);
      });
  };

  const jobRunButton = () => {
    return (
      <button
        onClick={runJob}
        className="smls-job-line-run-button"
        type="button"
        disabled={isRunButtonDisabled}
      >
        <img src={play} className="smls-job-play" alt="Job run" />
        Run Now
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
              disabled={isToggleDisabled}
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
          className={`smls-job-status smls-status-${statusValue.toLowerCase()}`}
        >
          {statusValue}
        </Badge>
      </Col>
      <Col sm={2}>{jobRunButton(id)}</Col>
      <Toast
        onClose={() => setShowNotification(false)}
        show={showNotification}
        delay={3000}
        autohide
        className="smls-toast-notificaiton"
      >
        <Toast.Header>
          <img src="holder.js/20x20?text=%20" className="rounded mr-2" alt="" />
          <strong className="mr-auto">Job starts executing...</strong>
        </Toast.Header>
      </Toast>
    </Row>
  );
};

export default JobLine;
