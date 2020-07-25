import React from 'react';
import PropTypes from 'prop-types';

import { Spinner } from 'react-bootstrap';
import moment from 'moment';

const Logs = ({ logs, loadingLogs }) => {
  if (loadingLogs) {
    return (
      <div className="smls-job-logs-loading-container">
        <Spinner animation="border" role="status" />
      </div>
    );
  }

  if (!logs.length) {
    return (
      <div className="smls-job-logs-initial-screen-container">
        Click Execution Timeline to see logs.
      </div>
    );
  }

  return (
    <div className="smls-job-container">
      {logs.map((log, i) => (
        <div key={i}>
          <span className="smls-job-logs-timestamp">
            {moment.utc(log.timestamp).format('YYYY-MM-DD HH:mm:ss')}
          </span>
          <span className="smls-job-logs-message">{log.message.trim()}</span>
        </div>
      ))}
    </div>
  );
};

export default Logs;

Logs.propTypes = {
  logs: PropTypes.array,
  loadingLogs: PropTypes.bool,
};

Logs.defaultProps = {
  logs: [],
  loadingLogs: null,
};
