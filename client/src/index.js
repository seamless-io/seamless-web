import 'regenerator-runtime/runtime'
import React from 'react';
import ReactDOM from 'react-dom';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
// import 'react-bootstrap-table/dist/react-bootstrap-table-all.min.css';

import './styles/style.css'
import './styles/toggleSwitch.css'
import './styles/jobExecutionSpinner.css'
import './styles/scroll.css'

import Jobs from './components/Jobs/Jobs';
import JobDetails from './components/Jobs/JobDetails/JobDetails';


const Application = () => {
  return (
    <Router>
      <div className="BackgroundContainer">
        <div className="MainContainer">
          <nav>
            <ul>
              <li>
                <Link to="/">Jobs</Link>
              </li>
              <li>
                <a href={window.location.origin + "/logout"}> Logout </a>
              </li>
            </ul>
          </nav>

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

ReactDOM.render(<Application />, document.getElementById('root'));
