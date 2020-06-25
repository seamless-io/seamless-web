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

import LoginForm from './components/LoginForm';
import Jobs from './components/Jobs';

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
              <Link to="/login">Login</Link>
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
        </Switch>
      </div>
    </Router>
  );
};

ReactDOM.render(<Application />, document.getElementById('root'));
