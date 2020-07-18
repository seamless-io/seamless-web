import React, { useState, useEffect } from 'react';
import { Row, Col, Spinner } from 'react-bootstrap';

import JobLineItem from './JobLineItem';

const ExecutionTimeline  = (props) => {

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
          {props.futureExecutions.map(exec => ( <JobLineItem execution={exec} /> ))}
          {timelineSeparator()}
          {props.recentExecutions.map(exec => ( <JobLineItem execution={exec} /> ))}
        </Col>
        <Col sm={8} className="smls-job-main-info-section">
          <Row>
            <Col sm={12}>
              <h5 className="smls-job-main-info-section-header">Logs</h5>
            </Col>
            <Col sm={12}>
              <div className="smls-job-container">logs....</div>
            </Col>
          </Row>
        </Col>
      </Row>
  )
}

export default ExecutionTimeline;
