import React from 'react';
import { Row, Col } from 'react-bootstrap';

const JobExecutionItem = props => {
  return (
    <Row>
      <Col>
        <div className="smls-job-info-section-col-scheduled">
          <div className="smls-job-info-section-col-scheduled-text">
            <span>{props.execution.created_at}</span>
          </div>
          <div className="smls-job-info-section-col-scheduled-badge">
            <span>{props.execution.status}</span>
          </div>
        </div>
      </Col>
    </Row>
  );
};

export default JobExecutionItem;
