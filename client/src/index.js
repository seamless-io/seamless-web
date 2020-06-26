import 'regenerator-runtime/runtime'
import React from 'react';
import ReactDOM from 'react-dom';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
import 'react-bootstrap-table/dist/react-bootstrap-table-all.min.css';

import Jobs from './components/Jobs';
import JobDetails from './components/Jobs/JobDetails';

const Application = () => {
  return (
    <Router>
      <div>
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
          <Route path="/login">
            <LoginForm />
          </Route>
          <Route path="/jobs/:id" component={JobDetails}>
          </Route>
        </Switch>
      </div>
    </Router>
  );
};

ReactDOM.render(<Application />, document.getElementById('root'));
