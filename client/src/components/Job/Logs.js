import React from 'react';
import { Spinner } from 'react-bootstrap';

const Logs = ({ logs, loadingLogs }) => {
  if (loadingLogs) {
    return (
      <div className="smls-job-logs-loading-container">
        <Spinner animation="border" role="status"></Spinner>
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
        <span key={i} style={{ display: 'block' }}>
          {log.message}
        </span>
      ))}
    </div>
  );
};

export default Logs;
