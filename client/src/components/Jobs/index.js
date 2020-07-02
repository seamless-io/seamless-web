import React, {Component} from 'react';
import JobsTable from "./JobsTable";
import openSocket from 'socket.io-client';

import '../../styles/style.css'
import {getJobRuns, getJobs} from "../../api";

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

    socket = openSocket('http://' + document.domain + ':' + location.port + '/socket');

    updateJobStatus = (data) => {
        let updated_jobs = this.state.jobs.slice();
        let job_index = updated_jobs.findIndex((obj => obj.id == data.job_id));

        updated_jobs[job_index].status = data.status;
        this.setState({...this.state, jobs: updated_jobs});
    }

    componentDidMount() {
        this.fetchJobs();
        this.socket.on('status', data => this.updateJobStatus(data));
    }

    fetchJobs = () => {
        this.setState({...this.state, isFetching: true});
        getJobs()
            .then(res => {
                this.setState({
                        jobs: res,
                        isFetching: false
                    })
            })
            .catch (err => {
                console.error(err)
                this.setState({...this.state, isFetching: false});
            })
    };
}
export default Jobs