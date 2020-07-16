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
  Spinner,
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
  const [showNotification, setShowNotification] = useState(false);

  if (scheduleValue === 'None') {
    setScheduleValue('Not scheduled');
    setScheduleClassName('smls-muted');
  }

  const openJob = () => {
    history.push(`jobs/${id}`);
  };

  const socket = openSocket(
    location.protocol + '//' + document.domain + ':' + location.port + '/socket'
  );

  useEffect(() => {
    socket.on('status', data => setStatusValue(data.status));
  });

  const runJob = () => {
    setShowNotification(true);
    setStatusValue('EXECUTING');
    triggerJobRun(id)
      .then(() => {})
      .catch(payload => {
        alert(payload);
      });
  };

  const runButtonContent = () => {
    if (statusValue === 'EXECUTING') {
      return (
        <Spinner
          as="span"
          animation="border"
          size="sm"
          role="status"
          aria-hidden="true"
        />
      );
    }

    return (
      <>
        <img src={play} className="smls-job-play" alt="Job run" />
        Run now
      </>
    );
  };

  const jobRunButton = () => {
    return (
      <button
        onClick={runJob}
        className="smls-job-line-run-button"
        type="button"
        disabled={statusValue === 'EXECUTING'}
      >
        {runButtonContent()}
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
          <strong className="mr-auto">{`${name} starts executing...`}</strong>
        </Toast.Header>
      </Toast>
    </Row>
  );
};

export default JobLine;
