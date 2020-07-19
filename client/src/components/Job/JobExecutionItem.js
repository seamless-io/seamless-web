import React from 'react';
import { Row, Col } from 'react-bootstrap';

const JobExecutionItem = ({ time, status, showLogs }) => {
  return (
    <Row className="smls-job-executiontimeline-time">
      <Col>
        <div
          className={`smls-job-info-section-execution-item smls-execution-${status.toLowerCase()}`}
          onClick={showLogs}
        >
          <div className="smls-job-info-section-execution-item-text">
            <span>{time}</span>
          </div>
          <div
            className={`smls-job-info-section-execution-item-badge smls-execution-badge-${status.toLowerCase()}`}
          >
            <span>{status}</span>
          </div>
        </div>
      </Col>
    </Row>
  );
};

export default JobExecutionItem;
