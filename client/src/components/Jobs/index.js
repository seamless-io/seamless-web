import React, {Component} from 'react';
import JobsTable from "./JobsTable";

import '../../styles/style.css'

const GET_JOBS_URL = '/api/v1/jobs'


class Jobs extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isFetching: false,
            jobs: []
        };
    }
    render() {
        return (
            <div>
                <h1 className="Header">My Jobs:</h1>
                <button className="ControlButton" onClick={this.fetchJobs}>
                    <span> Refresh </span>
                </button>
                <JobsTable data={this.state.jobs}/>
            </div>
        )
    }

    componentDidMount() {
        this.fetchJobs();
    }
    fetchJobs = () => {
        this.setState({...this.state, isFetching: true});
        fetch(GET_JOBS_URL)
            .then(response => response.json())
            .then(result => {
                this.setState({jobs: result, isFetching: false})
            })
            .catch(e => {
                console.log(e);
                this.setState({...this.state, isFetching: false});
            });
    };
}
export default Jobs