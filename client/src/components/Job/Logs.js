import React from 'react';
import { Spinner } from 'react-bootstrap';

const Logs = ({ logs, loadingLogs, initialScreen }) => {
  if (loadingLogs) {
    return (
      <div className="smls-job-logs-loading-container">
        <Spinner animation="border" role="status"></Spinner>
      </div>
    );
  }

  console.log(initialScreen);

  if (initialScreen) {
    return (
      <div className="smls-job-logs-initial-screen-container">
        Click Execution Timeline to see logs.
      </div>
    );
  }

  return (
    <div className="smls-job-container">
      {logs.map(log => (
        <span key={log.id} style={{ display: 'block' }}>
          {log.message}
        </span>
      ))}
    </div>
  );
};

export default Logs;
