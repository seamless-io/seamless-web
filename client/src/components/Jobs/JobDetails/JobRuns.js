import React, {Component} from "react";
import {getJobRunLogs, getJobRuns} from '../../../api';
import {BootstrapTable, TableHeaderColumn} from "react-bootstrap-table";
import JobRunLogs from "./JobRunLogs";
import ExecutionTimelineTable from "./ExecutionTimelineTable";

class JobRuns extends Component {
    constructor(props) {
        super(props);
        this.state = {
            job_id: props.job_id,
            isFetching: true,
            runs: [],
            selected_job_run_id: null,
            logs: []
        };
    }
    render() {
        return (
            <div>
                <p className="SubHeader">Execution Timeline</p>
                <ExecutionTimelineTable data={this.state.runs}/>
                <JobRunLogs logs={this.state.logs}
                            isFetching={this.state.isFetching}
                            handleRefreshClick={this.fetchLogs}/>

            </div>
        )
    }

    handleRowClick(row) {
        console.log(row);
        getJobRunLogs(row.job_id, row.id)
            .then(res => {
                console.log(res)
                this.setState({
                    isFetching: false,
                    selected_job_run_id: row.id,
                    logs: res
                });
            })
            .catch (err => console.error(err))
    }

    componentDidMount() {
        this.fetchRuns()
    }

    fetchRuns = () => {
        this.setState({
            isFetching: true,
            runs: [],
            selected_job_run_id: null
        });
        getJobRuns(this.state.job_id)
            .then(res => {
                console.log(res.slice(-1)[0].id)
                this.setState({
                    isFetching: false,
                    runs: res,
                });
            })
            .catch (err => console.error(err))
    }

    fetchLogs = () => {
        this.setState({
            isFetching: true,
            logs: []
        });
        getJobRunLogs(this.state.job_id, this.state.selected_job_run_id)
            .then(res => {
                console.log(res)
                this.setState({
                    isFetching: false,
                    logs: res
                });
            })
            .catch (err => console.error(err))
    }

}
export default JobRuns