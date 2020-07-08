import React from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

import { Container } from 'react-bootstrap';

import ApplicationHeader from './ApplicationHeader';
import Jobs from '../Jobs/Jobs';
import Account from '../Account/Account';
import JobDetails from '../Jobs/JobDetails/JobDetails';

import './style.css';

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
            <Route path="/account">
              <Account />
            </Route>
            <Route path="/jobs/:id" component={JobDetails}></Route>
          </Switch>
        </div>
      </Container>
    </Router>
  );
};

export default ApplicationRoot;
