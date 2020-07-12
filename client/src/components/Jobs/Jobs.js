import React, { Component } from 'react';
import openSocket from 'socket.io-client';
import { Row, Col } from 'react-bootstrap';

import { getJobs, updateJob } from '../../api';
import JobLine from './JobLine';

import './style.css';

import linkExternal from '../../images/link-external.svg';

class Jobs extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isFetching: false,
      jobs: [],
    };
  }

  render() {
    return (
      <>
        <Row className="smls-jobs-header">
          <Col className="smls-my-jobs-header">
            <h1 className="smls-my-jobs-h1">My Jobs</h1>
          </Col>
          <Col className="smls-jobs-header-buttons-container">
            <div className="smls-jobs-header-buttons">
              <button
                className="smls-button-add-jobs"
                onClick={() => alert('Not working yet.')}
              >
                <img src={linkExternal} alt="External link" />
                <span className="smls-jobs-leaen-add-jobs-text">
                  Learn how to create jobs
                </span>
              </button>
            </div>
          </Col>
        </Row>
        <Row className="smls-jobs-column-names">
          <Col sm={4}>NAME</Col>
          <Col sm={4}>SCHEDULE</Col>
          <Col sm={2}>STATUS</Col>
          <Col sm={2}>CONTROLS</Col>
        </Row>
        {this.state.jobs.map(job => (
          <JobLine key={job.id} {...job} />
        ))}
      </>
    );
  }

  updateJobById = (job_id, update_map) => {
    let updated_jobs = this.state.jobs.slice();
    let job_index = updated_jobs.findIndex(obj => obj.id == job_id);
    let job_to_update = updated_jobs[job_index];

    for (let key in update_map) {
      job_to_update[key] = update_map[key];
    }

    updated_jobs[job_index] = job_to_update;
    this.setState({ ...this.state, jobs: updated_jobs });
  };

  socket = openSocket(
    location.protocol + '//' + document.domain + ':' + location.port + '/socket'
  );

  updateJobStatus = data => {
    this.updateJobById(data.job_id, { status: data.status });
  };

  componentDidMount() {
    this.fetchJobs();
    this.socket.on('status', data => this.updateJobStatus(data));
  }

  fetchJobs = () => {
    this.setState({ ...this.state, isFetching: true });
    getJobs()
      .then(res => {
        this.setState({
          jobs: res,
          isFetching: false,
        });
      })
      .catch(err => {
        console.error(err);
        this.setState({ ...this.state, isFetching: false });
      });
  };

  updateSchedule = (job, schedule_exists, schedule_is_active) => {
    if (!schedule_exists) {
      return; // Ignore schedule switch clicks
    }
    if (schedule_is_active) {
      updateJob(job.id, { schedule_is_active: false });
      this.updateJobById(job.id, { schedule_is_active: 'False' });
    } else {
      updateJob(job.id, { schedule_is_active: true });
      this.updateJobById(job.id, { schedule_is_active: 'True' });
    }
  };
}

export default Jobs;
