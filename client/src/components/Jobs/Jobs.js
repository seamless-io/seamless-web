import React, {Component} from 'react';
import JobsTable from "./JobsTable";
import openSocket from 'socket.io-client';

import '../../styles/style.css'
import {getJobs, updateJob} from "../../api";

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
                <JobsTable data={this.state.jobs}
                           onScheduleSwitch={this.updateSchedule}/>
            </div>
        )
    }

    updateJobById = (job_id, update_map) => {
        let updated_jobs = this.state.jobs.slice();
        let job_index = updated_jobs.findIndex((obj => obj.id == job_id));
        let job_to_update = updated_jobs[job_index]

        for (let key in update_map) {
            job_to_update[key] = update_map[key]
        }

        updated_jobs[job_index] = job_to_update;
        this.setState({...this.state, jobs: updated_jobs});
    }

    socket = openSocket('http://' + document.domain + ':' + location.port + '/socket');

    updateJobStatus = (data) => {
        this.updateJobById(data.job_id, {'status': data.status})
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

    updateSchedule = (job, schedule_exists, schedule_is_active) => {
        if (!schedule_exists) {
            return; // Ignore schedule switch clicks
        }
        if (schedule_is_active) {
            updateJob(job.id, {'schedule_is_active': false})
            this.updateJobById(job.id, {'schedule_is_active': 'False'})
        } else {
            updateJob(job.id, {'schedule_is_active': true})
            this.updateJobById(job.id, {'schedule_is_active': 'True'})
        }
    }
}
export default Jobs