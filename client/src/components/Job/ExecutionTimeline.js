import React from 'react';

import { Row, Col, Spinner } from 'react-bootstrap';

import JobExecutionItem from './JobExecutionItem';

const ExecutionTimeline = props => {
  const renderExecutionTimeLine = () => {
    if (props.loadingExecutionTimeLine) {
      return (
        <div className="smls-job-executiontimeline-spinner-container">
          <Spinner animation="border" role="status"></Spinner>
        </div>
      );
    }

    return (
      <>
        {renderNextExecution(props.schedule)}
        {props.lastFiveExecutions.map(execution => (
          <JobExecutionItem
            key={execution.run_id}
            time={execution.created_at}
            status={execution.status}
          />
        ))}
      </>
    );
  };

  const renderNextExecution = schedule => {
    if (schedule !== 'Not scheduled') {
      return (
        <>
          <JobExecutionItem time={'2020-20-20'} status={'scheduled'} />
          <Row>
            <Col>
              <div className="smls-job-info-section-col-hr">
                <hr />
              </div>
            </Col>
          </Row>
        </>
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
        {renderExecutionTimeLine()}
      </Col>
    </Row>
  );
};

export default ExecutionTimeline;
