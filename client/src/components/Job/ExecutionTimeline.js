import React from 'react';

import { Row, Col, Spinner } from 'react-bootstrap';

import Logs from './Logs';
import JobExecutionItem from './JobExecutionItem';

const ExecutionTimeline = ({
  loadingExecutionTimeLine,
  lastFiveExecutions,
  nextExecution,
  logs,
  showLogs,
  loadingLogs,
  activeItem,
}) => {
  const renderExecutionTimeLine = () => {
    if (loadingExecutionTimeLine) {
      return (
        <div className="smls-job-executiontimeline-spinner-container">
          <Spinner animation="border" role="status"></Spinner>
        </div>
      );
    }

    return (
      <>
        {renderNextExecution()}
        {renderLastFiveExecutions()}
      </>
    );
  };

  const renderLastFiveExecutions = () => {
    if (lastFiveExecutions && lastFiveExecutions.length > 0) {
      return lastFiveExecutions.map(execution => (
        <JobExecutionItem
          key={execution.run_id}
          time={execution.created_at}
          status={execution.status}
          active={execution.run_id === activeItem}
          showLogs={() => showLogs(execution.run_id)}
        />
      ));
    }

    return (
      <div className="smls-job-executiontimelie-no-runs">
        This job was not run yet.
      </div>
    );
  };

  const renderNextExecution = () => {
    if (nextExecution !== 'Not scheduled') {
      return (
        <>
          <JobExecutionItem time={nextExecution} status={'scheduled'} />
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
      <Col sm={8} className="smls-job-main-info-section">
        <Row>
          <Col sm={12}>
            <h5>Logs</h5>
          </Col>
          <Col sm={12}>
            <Logs logs={logs} loadingLogs={loadingLogs} />
          </Col>
        </Row>
      </Col>
    </Row>
  );
};

export default ExecutionTimeline;
