import React from 'react';
import {
    Link
} from "react-router-dom";

const ApplicationHeader = () => {
    return (
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
    );
};

export default ApplicationHeader;
