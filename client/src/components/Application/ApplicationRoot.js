import React from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import Favicon from 'react-favicon';

import { Container } from 'react-bootstrap';

import favicon from '../../images/favicon.ico';

import ApplicationHeader from './ApplicationHeader';
import Jobs from '../Jobs/Jobs';
import Account from '../Account/Account';
import Job from '../Job/Job';
import CodeEditor from '../Job/CodeEditor';
import Guide from '../Guide/Guide';

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
            <Route exact path="/jobs/:id" component={Job}></Route>
            <Route exact path="/jobs/:id/ide" component={CodeEditor}></Route>
            <Route path="/guide">
              <Guide />
            </Route>
          </Switch>
        </div>
      </Container>
    </Router>
  );
};

export default ApplicationRoot;
