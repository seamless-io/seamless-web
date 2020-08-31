import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

import { Row, Col, Spinner, Modal } from 'react-bootstrap';
import Toggle from 'react-toggle';
import moment from 'moment';
import { AiOutlineCode } from 'react-icons/ai';

import { socket } from '../../socket';
import {
  getJob,
  triggerJobRun,
  enableJobSchedule,
  getLastExecutions,
  getNextJobExecution,
  getJobRunLogs,
} from '../../api';
import ExecutionTimeline from './ExecutionTimeline';
import WebIde from '../WebIde/WebIde';
import Notification from '../Notification/Notification';

import './style.css';
import '../Jobs/toggle.css';
import download from '../../images/cloud-download.svg';
import timeHistory from '../../images/time-history.svg';

const Job = () => {
  const job = useParams();
  const downloadJobLink = `/api/v1/jobs/${job.id}/code`;
  const [name, setName] = useState('');
  const [schedule, setSchedule] = useState('');
  const [isScheduleOn, setIsScheduleOn] = useState(false);
  const [isToggleDisabled, setIsToggleDisabled] = useState(true);
  const [loading, setLoading] = useState(true);
  const [statusValue, setStatusValue] = useState(null);
  const [lastFiveExecutions, setLastFiveExecutions] = useState([]);
  const [loadingExecutionTimeLine, setLoadingExecutionTimeLine] = useState(
    true
  );
  const [nextExecution, setNextExecution] = useState('');
  const [updatedAt, setUpdatedAt] = useState('');
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [activeItem, setActiveItem] = useState(null);
  const [loadingStreamingLogs, setLoadingStreamingLogs] = useState(false);
  const [loadingToggleSwitch, setLoadingToggleSwitch] = useState(false);
  const [streamingLogs, setStreamingLogs] = useState([]);
  const [historyLogs, setHistoryLogs] = useState([]);
  const [statusRun, setStatusRun] = useState('');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');
  const [showCode, setShowCode] = useState(false);

  const displayNotification = (show, title, body, alterType) => {
    setShowNotification(show);
    setNotificationTitle(title);
    setNotificationBody(body);
    setNotificationAlertType(alterType);
  };

  const closeNotification = () => {
    setShowNotification(false);
  };

  const updateJobStatus = jobRunning => {
    if (jobRunning.job_id === job.id) {
      setActiveItem(Number(jobRunning.job_run_id));
      setStatusValue(jobRunning.status);
      setLoadingStreamingLogs(jobRunning.status === 'EXECUTING');
    }
  };

  const updateJobLogs = jobLogLine => {
    if (jobLogLine.job_id === job.id) {
      setStreamingLogs(jobLogs => [...jobLogs, jobLogLine]);
    }
  };

  useEffect(() => {
    socket.on('status', jobRunning => updateJobStatus(jobRunning));
    socket.on('logs', jobLogLine => updateJobLogs(jobLogLine));
  }, []);

  const handleToggleSwitch = e => {
    setLoadingToggleSwitch(true);
    setIsScheduleOn(e.target.checked);
    enableJobSchedule(job.id, e.target.checked)
      .then(() => {
        setLoadingToggleSwitch(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to toggle the switch :(',
          'danger'
        );
      });
  };

  const loadToggleSwitch = () => {
    if (loadingToggleSwitch) {
      return (
        <div className="smls-job-toggle-switch-container">
          <Spinner
            animation="border"
            role="status"
            size="sm"
            style={{ marginBottom: '8px' }}
          />
        </div>
      );
    }
  };

  useEffect(() => {
    setLoading(true);
    getJob(job.id)
      .then(payload => {
        setName(payload.name);
        setStatusValue(payload.status);
        setUpdatedAt(
          moment.utc(payload.updated_at).format('MMM DD, YYYY, HH:mm')
        );
        setIsScheduleOn(payload.schedule_is_active === 'True');
        setIsToggleDisabled(payload.aws_cron === 'None');
        setSchedule(
          payload.human_cron === 'None' ? 'Not scheduled' : payload.human_cron
        );
        setLoading(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          "Unable to fetch job's details :(",
          'danger'
        );
      });
  }, []);

  useEffect(() => {
    setLoadingExecutionTimeLine(true);
    getLastExecutions(job.id)
      .then(payload => {
        setLastFiveExecutions(payload.last_executions);
        setLoadingExecutionTimeLine(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to fetch last five executions :(',
          'danger'
        );
      });
  }, [statusValue]);

  useEffect(() => {
    getNextJobExecution(job.id)
      .then(payload => {
        setNextExecution(payload.result);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to fetch the next execution details :(',
          'danger'
        );
      });
  }, []);

  const runJob = () => {
    setStreamingLogs([]);
    setStatusRun('EXECUTING');
    setLoadingExecutionTimeLine(true);
    setLoadingStreamingLogs(true);
    triggerJobRun(job.id)
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
        <span className="smls-job-run-button-text">Run</span>
      </>
    );
  };

  const showLogs = (runId, status) => {
    setStatusRun(status);
    setLoadingStreamingLogs(status === 'EXECUTING');
    setLoadingLogs(true);
    setActiveItem(runId);
    getJobRunLogs(job.id, runId)
      .then(payload => {
        setHistoryLogs(
          payload.sort(function (a, b) {
            var dateA = new Date(a.timestamp),
              dateB = new Date(b.timestamp);
            return dateA - dateB;
          })
        );
        setLoadingLogs(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to fetch logs :(',
          'danger'
        );
      });
  };

  const openIde = () => {
    setShowCode(!showCode);
  };

  if (loading) {
    return (
      <div className="smls-jobs-spinner-container">
        <Spinner animation="border" role="status" />
      </div>
    );
  }

  return (
    <>
      <Row className="smls-job-header">
        <Col className="smls-job-name-header">
          <div className="smls-job-heade-container">
            <h1 className="smls-job-name-h1">{name}</h1>
          </div>
        </Col>
        <Col className="smls-job-header-buttons-container">
          <div className="smls-job-header-buttons">
            <button
              className="smls-job-run-button"
              type="button"
              disabled={statusValue === 'EXECUTING'}
              onClick={runJob}
            >
              {runButtonContent()}
            </button>
            <button
              className="smls-job-web-ide-button"
              type="button"
              onClick={openIde}
            >
              <AiOutlineCode />
              <span className="smls-job-web-ide-button-text">Show Code</span>
            </button>
            <a href={downloadJobLink}>
              <button className="smls-job-download-code-button" type="button">
                <img src={download} alt="Download code" />
                <span className="smls-job-download-code-button-text">
                  Download Code
                </span>
              </button>
            </a>
          </div>
        </Col>
      </Row>
      <Row className="smls-job-extra-info">
        <Col style={{ paddingLeft: '0px' }}>
          <div
            className="smls-job-extra-info-section"
            style={{ position: 'absolute' }}
          >
            <Toggle
              checked={isScheduleOn}
              icons={false}
              disabled={isToggleDisabled}
              onChange={handleToggleSwitch}
            />
            <span className={!isScheduleOn ? 'smls-muted' : ''}>
              {schedule} UTC
            </span>
          </div>
          {loadToggleSwitch()}
        </Col>
        <Col style={{ paddingRight: '0px' }}>
          <div className="smls-job-extra-info-section">
            <img src={timeHistory} alt="Updated at" />
            <span>{`Code updated on ${updatedAt} UTC`}</span>
          </div>
        </Col>
      </Row>
      <ExecutionTimeline
        loadingExecutionTimeLine={loadingExecutionTimeLine}
        lastFiveExecutions={lastFiveExecutions}
        nextExecution={nextExecution}
        logs={statusRun === 'EXECUTING' ? streamingLogs : historyLogs}
        showLogs={showLogs}
        loadingLogs={loadingLogs}
        activeItem={activeItem}
        loadingStreamingLogs={loadingStreamingLogs}
      />
      <Notification
        show={showNotification}
        closeNotification={closeNotification}
        title={notificationTitle}
        body={notificationBody}
        alertType={notificationAlertType}
      />

      <Modal
        show={showCode}
        onHide={() => setShowCode(!showCode)}
        dialogClassName="smls-web-ide-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>{name}</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ paddingTop: '0px' }}>
          <WebIde jobId={job.id} />
        </Modal.Body>
      </Modal>
    </>
  );
};

export default Job;
