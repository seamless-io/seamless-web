import React, { useState, useEffect } from 'react';
import { Row, Col, Spinner } from 'react-bootstrap';

const JobLineItem = (execution) => {
  return (
    <Row>
        <Col>
          <div className="smls-job-info-section-col-scheduled">
            <div className="smls-job-info-section-col-scheduled-text">
              <span>{execution.run_datetime}</span>
            </div>
            <div className="smls-job-info-section-col-scheduled-badge">
              <span>{execution.status}</span>
            </div>
          </div>
        </Col>
      </Row>
  )
}

export default JobLineItem;
