import React, { useState, useEffect } from 'react';

import { Row, Col, Spinner } from 'react-bootstrap';
import { AiOutlineThunderbolt, AiOutlineCode } from 'react-icons/ai';

import { getJobs, getUserInfo } from '../../api';
import JobLine from './JobLine';
import Notification from '../Notification/Notification';

import './style.css';

const Jobs = () => {
  const [jobs, setjobs] = useState([]);
  const [noJobsStyle, setNoJobsStyle] = useState('');
  const [loading, setLoading] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');

  const displayNotification = (show, title, body, alterType) => {
    setShowNotification(show);
    setNotificationTitle(title);
    setNotificationBody(body);
    setNotificationAlertType(alterType);
  };

  const closeNotification = () => {
    setShowNotification(false);
  };

  useEffect(() => {
    getUserInfo()
      .then(payload => {
        setApiKey(payload.api_key);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          "Unable to fetch user's details :(",
          'danger'
        );
      });
  }, []);

  useEffect(() => {
    setLoading(true);
    getJobs()
      .then(payload => {
        setjobs(payload);
        setNoJobsStyle(
          payload && payload.length > 0 ? '' : 'smls-no-jobs-header'
        );
        setLoading(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to fetch jobs :(',
          'danger'
        );
      });
  }, []);

  const renderJobs = () => {
    if (jobs && jobs.length > 0) {
      return (
        <>
          <Row className="smls-jobs-column-names">
            <Col sm={4}>NAME</Col>
            <Col sm={4}>SCHEDULE</Col>
            <Col sm={2}>STATUS</Col>
            <Col sm={2}>CONTROLS</Col>
          </Row>
          {jobs.map(job => (
            <JobLine key={job.id} {...job} />
          ))}
        </>
      );
    }

    return (
      <>
        <Row className="smls-no-jobs">
          <Col className="smls-no-jobs-icon-container">
            <div className="smls-no-jobs-icon blue">
              <AiOutlineThunderbolt size={24} style={{ color: '#007bff' }} />
            </div>
            <div className="smls-no-jobs-message">
              <div>
                <strong>You have no jobs</strong>
              </div>
              <div>
              Navigate to the Templates tab to add your first Job.
               </div>
               <div>
               If you're new to Seamless Cloud, you should choose the "Example Job" template which is at the top of the list.
               </div>
            </div>
          </Col>
        </Row>
      </>
    );
  };

  if (loading) {
    return (
      <div className="smls-jobs-spinner-container">
        <Spinner animation="border" role="status" />
      </div>
    );
  }

  return (
    <>
      <Row className={`smls-jobs-header ${noJobsStyle}`}>
        <Col className="smls-my-jobs-header">
          <h1 className="smls-my-jobs-h1">My Jobs</h1>
        </Col>
      </Row>
      {renderJobs()}
      <Notification
        show={showNotification}
        closeNotification={closeNotification}
        title={notificationTitle}
        body={notificationBody}
        alertType={notificationAlertType}
      />
    </>
  );
};

export default Jobs;
