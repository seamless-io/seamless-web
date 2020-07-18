import React, { useState, useEffect } from 'react';
import { Row, Col, Spinner } from 'react-bootstrap';

import { getJobRunLogs } from '../../api';

import JobLineItem from './JobLineItem';
import Logs from './Logs';

const ExecutionTimeline = (props) => {

  const [logs, setLogs] = useState('logs...');
  
  useEffect(() => {
    if (props.recentExecutions && props.recentExecutions.length > 0) {
      var last_exec = props.recentExecutions[0];
      updateLogs(last_exec.run_id);
    }
  }, [props.recentExecutions]);

  const timelineSeparator = () => {
    if (props.futureExecutions && props.futureExecutions.length > 0) {
      return (
        <Row>
          <Col>
            <div className="smls-job-info-section-col-hr">
              <hr />
            </div>
          </Col>
        </Row>
      );
    }
  };

  const updateLogs = (run_id) => {
    getJobRunLogs(props.job_id, run_id)
      .then(payload => {
        var msgs = [];
        for (const item of payload) {
          msgs.push(item.message);
        }
        setLogs(msgs);
      })
      .catch((something) => {
        alert('errors!');
      });
  }

  return (
    <Row className="smls-job-main-info">
        <Col
          sm={4}
          className="smls-job-main-info-section"
          style={{ borderRight: '2px solid #ebedf0' }}
        >
          <Row>
            <Col>
              <div className="smls-job-info-section-col">
                <h5>Execution Timeline</h5>
              </div>
            </Col>
          </Row>
          {props.futureExecutions.map(exec => (
            <JobLineItem execution={exec} />
          ))}
          {timelineSeparator()}
          {props.recentExecutions.map(exec => (
            <span onClick={() => updateLogs(exec.run_id) }>
              <JobLineItem execution={exec} />
            </span>
          ))}
        </Col>
        <Logs logs={logs} />
      </Row>
  )
}

export default ExecutionTimeline;
