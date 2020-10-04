import React from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import Favicon from 'react-favicon';

import { Container } from 'react-bootstrap';

import favicon from '../../images/favicon.ico';

import ApplicationHeader from './ApplicationHeader';
import Jobs from '../Jobs/Jobs';
import Account from '../Account/Account';
import Job from '../Job/Job';
import CLI from '../FAQ/CLI';
import JobTemplates from '../FAQ/JobTemplates';
import Templates from '../Templates/Templates';

import './style.css';

const ApplicationRoot = () => {
  return (
    <Router>
      <Favicon url={favicon} />
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
            <Route path="/templates">
              <Templates />
            </Route>
            <Route path="/faq/cli">
              <CLI />
            </Route>
            <Route path="/faq/templates">
              <JobTemplates />
            </Route>
            <Route exact path="/jobs/:id" component={Job}></Route>
          </Switch>
        </div>
      </Container>
    </Router>
  );
};

export default ApplicationRoot;
