import React from 'react';
import { Row, Col } from 'react-bootstrap';

const JobExecutionItem = ({ time, status, showLogs, active }) => {
  return (
    <Row className="smls-job-executiontimeline-time">
      <Col>
        <div
          className={`smls-job-info-section-execution-item ${
            active ? 'smls-execution-active-itme-' + status.toLowerCase() : ''
          }`}
          onClick={showLogs}
        >
          <div className="smls-job-info-section-execution-item-text">
            <span>{time}</span>
          </div>
          <div className="smls-job-info-section-execution-item-badge">
            <span className={`smls-execution-badge-${status.toLowerCase()}`}>
              {status}
            </span>
          </div>
        </div>
      </Col>
    </Row>
  );
};

export default JobExecutionItem;
