import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';

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

import { socket } from '../../socket';
import { triggerJobRun, enableJobSchedule } from '../../api';

import './toggle.css';
import play from '../../images/play-filled.svg';

const JobLine = ({ name, human_cron, status, id, schedule_is_active }) => {
  const history = useHistory();
  const [statusValue, setStatusValue] = useState(status);
  const [isScheduleOn, setIsScheduleOn] = useState(
    schedule_is_active === 'True'
  );
  const [showNotification, setShowNotification] = useState(false);

  const openJob = () => {
    history.push(`jobs/${id}`);
  };

  useEffect(() => {
    socket.on('status', job => updateJobStatus(job));
  }, []);

  const updateJobStatus = job => {
    if (job.job_id === id) {
      setStatusValue(job.status);
    }
  };

  const runJob = () => {
    setShowNotification(true);
    setStatusValue('EXECUTING');
    triggerJobRun(id)
      .then(() => {})
      .catch(payload => {
        alert(payload); // TODO: create a notification component
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

  const handleToggleSwitch = e => {
    setIsScheduleOn(e.target.checked);
    enableJobSchedule(id, e.target.checked)
      .then(payload => {
        alert(`Job "${name}" turned ${!isScheduleOn ? 'on' : 'off'}`); // TODO: create a notification component
      })
      .catch(payload => {
        alert('Something went wrong...'); // TODO: create a notification component
      });
  };

  const showTooltipContent = () => {
    if (human_cron === 'None') {
      return 'Needs to be triggered manually';
    }

    return `Job is ${isScheduleOn ? 'on' : 'off'}`;
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
              {showTooltipContent()}
            </Tooltip>
          }
        >
          <div className="smls-job-line-toggle-container">
            <Toggle
              defaultChecked={isScheduleOn}
              disabled={human_cron === 'None'}
              icons={false}
              onChange={handleToggleSwitch}
            />
            <span
              className={`smls-job-line-schedule ${
                human_cron === 'None' ? 'smls-muted' : ''
              }`}
            >
              {human_cron === 'None' ? 'Not scheduled' : human_cron}
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
