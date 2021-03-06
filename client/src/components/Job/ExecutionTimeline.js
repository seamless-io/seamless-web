import React from 'react';
import PropTypes from 'prop-types';

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
  loadingStreamingLogs,
}) => {
  const renderNextExecution = () => {
    if (nextExecution && nextExecution !== 'Not scheduled') {
      return (
        <>
          <JobExecutionItem time={nextExecution} status="scheduled" />
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

  const renderLastFiveExecutions = () => {
    if (lastFiveExecutions && lastFiveExecutions.length > 0) {
      return lastFiveExecutions.map(execution => (
        <JobExecutionItem
          key={execution.run_id}
          time={execution.created_at}
          status={execution.status}
          active={execution.run_id === activeItem}
          showLogs={() => showLogs(execution.run_id, execution.status)}
        />
      ));
    }

    return (
      <div className="smls-job-executiontimelie-no-runs">
        This job was not run yet.
      </div>
    );
  };

  const renderExecutionTimeLine = () => {
    if (loadingExecutionTimeLine) {
      return (
        <div className="smls-job-executiontimeline-spinner-container">
          <Spinner animation="border" role="status" />
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

  const loadStreamingLogs = () => {
    if (loadingStreamingLogs) {
      return (
        <Spinner
          animation="border"
          role="status"
          size="sm"
          style={{ marginBottom: '8px' }}
        />
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
              <h5 className="smls-job-small-header">Execution Timeline</h5>
            </div>
          </Col>
        </Row>
        {renderExecutionTimeLine()}
      </Col>
      <Col sm={8} className="smls-job-main-info-section">
        <Row>
          <Col sm={12}>
            <div className="smls-job-executiontimeline-logs-header">
              <h5 className="smls-job-small-header">Logs</h5>
              {loadStreamingLogs()}
            </div>
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

ExecutionTimeline.propTypes = {
  loadingExecutionTimeLine: PropTypes.bool,
  lastFiveExecutions: PropTypes.array,
  nextExecution: PropTypes.string,
  logs: PropTypes.array,
  showLogs: PropTypes.func,
  loadingLogs: PropTypes.bool,
  activeItem: PropTypes.number,
  loadingStreamingLogs: PropTypes.bool,
};

ExecutionTimeline.defaultProps = {
  loadingExecutionTimeLine: true,
  lastFiveExecutions: [],
  nextExecution: '',
  logs: [],
  showLogs: null,
  loadingLogs: false,
  activeItem: null,
  loadingStreamingLogs: true,
};
