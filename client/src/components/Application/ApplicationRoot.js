import React from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

import { Container } from 'react-bootstrap';

import './style.css';

import ApplicationHeader from './ApplicationHeader';
import Jobs from '../Jobs/Jobs';
import JobDetails from '../Jobs/JobDetails/JobDetails';

const ApplicationRoot = () => {
  return (
    <Router>
      <ApplicationHeader />

      <Container fluid className="smls-main-container">
        <div className="smls-jobs-container">
          <Switch>
            <Route exact path="/">
              <Jobs />
            </Route>
            <Route path="/jobs/:id" component={JobDetails}></Route>
          </Switch>
        </div>
      </Container>
    </Router>
  );
};

export default ApplicationRoot;
