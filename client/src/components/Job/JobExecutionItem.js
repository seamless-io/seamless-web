import React from 'react';
import PropTypes from 'prop-types';

import { Row, Col } from 'react-bootstrap';
import moment from 'moment';

const JobExecutionItem = ({ time, status, showLogs, active }) => {
  return (
    <Row className="smls-job-executiontimeline-time">
      <Col>
        <div
          className={`smls-job-info-section-execution-item ${
            active ? `smls-execution-active-itme-${status.toLowerCase()}` : ''
          }`}
          onClick={showLogs}
          role="button"
        >
          <div className="smls-job-info-section-execution-item-text">
            <span>{moment.utc(time).format('MMMM D, YYYY, HH:mm:ss')}</span>
          </div>
          <div className="smls-job-info-section-execution-item-badge">
            <span className={`smls-execution-badge-${status.toLowerCase()}`}>
              {status}
            </span>
          </div>
        </div>
      </Col>
    </Row>
  );
};

export default JobExecutionItem;

JobExecutionItem.propTypes = {
  time: PropTypes.string,
  status: PropTypes.string,
  showLogs: PropTypes.func,
  active: PropTypes.bool,
};

JobExecutionItem.defaultProps = {
  time: '',
  status: '',
  showLogs: null,
  active: null,
};
