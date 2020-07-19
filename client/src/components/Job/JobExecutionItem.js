import React from 'react';
import { Row, Col } from 'react-bootstrap';

const JobExecutionItem = ({ time, status }) => {
  return (
    <Row className="smls-job-executiontimeline-time">
      <Col>
        <div className="smls-job-info-section-col-scheduled">
          <div className="smls-job-info-section-col-scheduled-text">
            <span>{time}</span>
          </div>
          <div className="smls-job-info-section-col-scheduled-badge">
            <span>{status}</span>
          </div>
        </div>
      </Col>
    </Row>
  );
};

export default JobExecutionItem;
