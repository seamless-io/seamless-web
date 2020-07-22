import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

import { Row, Col, Spinner } from 'react-bootstrap';
import Toggle from 'react-toggle';
import moment from 'moment';

import { socket } from '../../socket';
import {
  getJob,
  triggerJobRun,
  enableJobSchedule,
  disableJobSchedule,
  getLastExecutions,
  getNextJobExecution,
  getJobRunLogs,
} from '../../api';
import ExecutionTimeline from './ExecutionTimeline';

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
  const [loading, setLoading] = useState(null);
  const [statusValue, setStatusValue] = useState(null);
  const [logs, setLogs] = useState([]);
  const [lastFiveExecutions, setLastFiveExecutions] = useState([]);
  const [loadingExecutionTimeLine, setLoadingExecutionTimeLine] = useState(
    false
  );
  const [nextExecution, setNextExecution] = useState('');
  const [updatedAt, setUpdatedAt] = useState('');
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [activeItem, setActiveItem] = useState(null);
  const [loadingStreamingLogs, setLoadingStreamingLogs] = useState(false);

  useEffect(() => {
    socket.on('status', jobRunning => updateJobStatus(jobRunning));
    socket.on('logs', jobLogLine => updateJobLogs(jobLogLine));
  }, []);

  const updateJobStatus = jobRunning => {
    if (jobRunning.job_id === job.id) {
      setActiveItem(Number(jobRunning.job_run_id));
      setStatusValue(jobRunning.status);
      setLoadingStreamingLogs(jobRunning.status === 'EXECUTING');
    }
  };

  const updateJobLogs = jobLogLine => {
    if (jobLogLine.job_id === job.id) {
      setLogs(logs => [...logs, jobLogLine]);
    }
  };

  const handleToggleSwitch = e => {
    var initialScheduleOn = isScheduleOn;

    setIsScheduleOn(!isScheduleOn);
    if (!e.target.checked) {
      disableJobSchedule(job.id).catch(error => {
        console.log('Error disabling a job...\n', error);
        setIsScheduleOn(initialScheduleOn);
      });
    } else {
      enableJobSchedule(job.id).catch(error => {
        console.log('Error enabling a job...\n', error);
        setIsScheduleOn(initialScheduleOn);
      });
    }
  };

  useEffect(() => {
    setLoading(true);
    getJob(job.id)
      .then(payload => {
        setName(payload.name);
        setStatusValue(payload.status);
        setUpdatedAt(moment(payload.updated_at).format('MMM DD, YYYY, HH:mm'));
        setIsScheduleOn(payload.schedule_is_active === 'True');
        setIsToggleDisabled(payload.aws_cron === 'None');
        setSchedule(
          payload.human_cron === 'None' ? 'Not scheduled' : payload.human_cron
        );
        setLoading(false);
      })
      .catch(() => {
        alert('Error!'); // TODO: create a notification component
      });
  }, []);

  useEffect(() => {
    getLastExecutions(job.id)
      .then(payload => {
        setLastFiveExecutions(payload.last_executions);
        setLoadingExecutionTimeLine(false);
      })
      .catch(() => {
        alert('Error!'); // TODO: create a notification component
      });
  }, [statusValue]);

  useEffect(() => {
    getNextJobExecution(job.id)
      .then(payload => {
        setNextExecution(payload.result);
      })
      .catch(() => {
        alert('Error!'); // TODO: create a notification component
      });
  }, []);

  const runJob = () => {
    setLogs([]);
    setLoadingExecutionTimeLine(true);
    setLoadingStreamingLogs(true);
    triggerJobRun(job.id)
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
        <span className="smls-job-run-button-text">Run</span>
      </>
    );
  };

  const showLogs = run_id => {
    setLoadingLogs(true);
    setActiveItem(run_id);
    getJobRunLogs(job.id, run_id)
      .then(payload => {
        setLogs(payload);
        setLoadingLogs(false);
      })
      .catch(payload => {
        alert(payload); // TODO: create a notification component
      });
  };

  if (loading) {
    return (
      <div className="smls-jobs-spinner-container">
        <Spinner animation="border" role="status"></Spinner>
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
            <a href={downloadJobLink}>
              <button className="smls-job-download-code-button">
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
          <div className="smls-job-extra-info-section">
            <Toggle
              checked={isScheduleOn}
              icons={false}
              disabled={isToggleDisabled}
              onChange={handleToggleSwitch}
            />
            <span className={!isScheduleOn ? 'smls-muted' : ''}>
              {schedule}
            </span>
          </div>
        </Col>
        <Col style={{ paddingRight: '0px' }}>
          <div className="smls-job-extra-info-section">
            <img src={timeHistory} alt="Updated at" />
            <span>{`Code updated on ${updatedAt}`}</span>
          </div>
        </Col>
      </Row>
      <ExecutionTimeline
        loadingExecutionTimeLine={loadingExecutionTimeLine}
        lastFiveExecutions={lastFiveExecutions}
        nextExecution={nextExecution}
        logs={logs}
        showLogs={showLogs}
        loadingLogs={loadingLogs}
        activeItem={activeItem}
        loadingStreamingLogs={loadingStreamingLogs}
      />
    </>
  );
};

export default Job;
