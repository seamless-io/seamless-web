import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';

import {
  Row,
  Col,
  Badge,
  OverlayTrigger,
  Tooltip,
  Spinner,
} from 'react-bootstrap';
import Toggle from 'react-toggle';

import Notification from '../Notification/Notification';
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
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');
  const [loadingToggleSwitch, setLoadingToggleSwitch] = useState(false);

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

  const displayNotification = (show, title, body, alterType) => {
    setShowNotification(show);
    setNotificationTitle(title);
    setNotificationBody(body);
    setNotificationAlertType(alterType);
  };

  const runJob = () => {
    displayNotification(
      true,
      'Launched!',
      `Job "${name}" starts executing.`,
      'info'
    );

    setStatusValue('EXECUTING');
    triggerJobRun(id)
      .then(() => {})
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to execute the job :(',
          'danger'
        );
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
    setLoadingToggleSwitch(true);
    setIsScheduleOn(e.target.checked);
    enableJobSchedule(id, e.target.checked)
      .then(() => {
        displayNotification(
          true,
          `Turned ${!isScheduleOn ? 'on' : 'off'}!`,
          `Job "${name}" turned ${!isScheduleOn ? 'on' : 'off'}`,
          'success'
        );
        setLoadingToggleSwitch(false);
      })
      .catch(() => {
        setLoadingToggleSwitch(false);
        displayNotification(
          true,
          'Ooops!',
          'Unable to toggle the switch :(',
          'danger'
        );
      });
  };

  const showTooltipContent = () => {
    if (human_cron === 'None') {
      return 'Needs to be triggered manually';
    }

    return `Job is ${isScheduleOn ? 'on' : 'off'}`;
  };

  const closeNotification = () => {
    setShowNotification(false);
  };

  const loadToggleSwitch = () => {
    if (loadingToggleSwitch) {
      return (
        <Col sm={12}>
          <div className="smls-job-line-toggle-switch-container">
            <Spinner
              animation="border"
              role="status"
              size="sm"
              style={{ marginBottom: '8px' }}
            />
          </div>
        </Col>
      );
    }

    return (
      <>
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
                {human_cron === 'None' ? 'Not scheduled' : `${human_cron} UTC`}
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
      </>
    );
  };

  return (
    <Row className="smls-job-line">
      {loadToggleSwitch()}
      <Notification
        show={showNotification}
        closeNotification={closeNotification}
        title={notificationTitle}
        body={notificationBody}
        alertType={notificationAlertType}
      />
    </Row>
  );
};

export default JobLine;
