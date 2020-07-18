import React, { useState, useEffect } from 'react';
import { Row, Col, Spinner } from 'react-bootstrap';


const Logs = (props) => {
  
  return (
    <Col sm={8} className="smls-job-main-info-section">
      <Row>
        <Col sm={12}>
          <h5 className="smls-job-main-info-section-header">Logs</h5>
        </Col>
        <Col sm={12}>
          <div className="smls-job-container">{props.logs}</div>
        </Col>
      </Row>
    </Col>
  )
}

export default Logs;
