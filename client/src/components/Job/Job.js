import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

import { Row, Col, Spinner } from 'react-bootstrap';
import Toggle from 'react-toggle';

import { socket } from '../../socket';
import { getJob, triggerJobRun } from '../../api';
import ExecutionTimeline from './ExecutionTimeline';

import './style.css';
import '../Jobs/toggle.css';
import download from '../../images/cloud-download.svg';
import timeHistory from '../../images/time-history.svg';
import pencil from '../../images/pencil-create.svg';

const Job = () => {
  const job = useParams();
  const downloadJobLink = `/api/v1/jobs/${job.id}/code`;
  const [name, setName] = useState('');
  const [schedule, setSchedule] = useState('');
  const [isScheduleOn, setIsScheduleOn] = useState(false);
  const [isToggleDisabled, setIsToggleDisabled] = useState(true);
  const [scheduleClassName, setScheduleClassName] = useState('');
  const [loading, setLoading] = useState(null);
  const [statusValue, setStatusValue] = useState(null);
  const [runDateTime, setRunDateTime] = useState(null);
  const [logs, setLogs] = useState([]);
  const [recentExecutions, setRecentExecutions] = useState([]);
  const [futureExecutions, setFutureExecutions] = useState([]);

  useEffect(() => {
    socket.on('status', jobRunning => updateJobStatus(jobRunning));
    socket.on('logs', jobLogLine => updateJobLogs(jobLogLine));
  }, []);

  const updateJobStatus = jobRunning => {
    if (jobRunning.job_id === job.id) {
      setStatusValue(jobRunning.status);
    }
  };

  const updateJobLogs = jobLogLine => {
    if (jobLogLine.job_id === job.id) {
      setLogs(logs => [...logs, jobLogLine.log_line]);
    }
  };

  useEffect(() => {
    setLoading(true);
    getJob(job.id)
      .then(payload => {
        setName(payload.name);
        setStatusValue(payload.status);
        setRunDateTime(payload.created_at);

        setRecentExecutions([
          ...recentExecutions,
          {
            status: statusValue,
            run_datetime: runDateTime,
          },
        ]);

        if (payload.human_cron === 'None') {
          setSchedule('Not scheduled');
          setScheduleClassName('smls-muted');
        }

        setLoading(false);
      })
      .catch(() => {
        alert('Error!');
      });
  }, []);

  const runJob = () => {
    setStatusValue('EXECUTING');
    setLogs([]);
    triggerJobRun(job.id)
      .then(() => {})
      .catch(payload => {
        alert(payload); // TODO: do not show on production
      });

    // TODO: fetch jobRunId from `triggerJobRun` and provide it here
    // setRecentExecutions([
    //   ...recentExecutions,
    //   {
    //     status: statusValue,
    //     run_datetime: runDateTime
    //   }
    // ]);
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
            <button
              className="smls-job-name-pencil"
              onClick={() => alert('Not working yet.')}
            >
              <img src={pencil} alt="Updated at" />
            </button>
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
              defaultChecked={isScheduleOn}
              icons={false}
              disabled={isToggleDisabled}
              onChange={() => alert('Not working yet.')}
            />
            <span className={scheduleClassName}>{schedule}</span>
          </div>
        </Col>
        <Col style={{ paddingRight: '0px' }}>
          <div className="smls-job-extra-info-section">
            <img src={timeHistory} alt="Updated at" />
            <span>Code updated on May 19, 2020, 14:56</span>
          </div>
        </Col>
      </Row>
      <ExecutionTimeline
        recentExecutions={recentExecutions}
        futureExecutions={futureExecutions}
      />
    </>
  );
};

export default Job;
