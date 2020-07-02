import React from 'react';
import {
    BrowserRouter as Router,
    Switch,
    Route
} from "react-router-dom";

import './styles/application.css'

import ApplicationHeader from './ApplicationHeader';
import Jobs from '../Jobs/Jobs';
import JobDetails from '../Jobs/JobDetails';


const ApplicationRoot = () => {
  return (
    <Router>
      <div className="BackgroundContainer">
        <div className="MainContainer">
          <ApplicationHeader />

          <Switch>
            <Route exact path="/">
              <Jobs />
            </Route>
            <Route path="/jobs/:id" component={JobDetails}>
            </Route>
          </Switch>
        </div>
      </div>
    </Router>
  );
};

export default ApplicationRoot;
