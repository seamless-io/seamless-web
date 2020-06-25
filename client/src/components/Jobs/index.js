import React, {Component} from 'react';
import JobsTable from "./JobsTable";

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
                <h1>My Jobs:</h1>
                <button className="btn btn-primary pull-right" onClick={this.fetchJobs}>
                    <span className="glyphicon glyphicon-refresh" /> Refresh
                </button>
                <JobsTable data={this.state.jobs}
                           isFetching={this.state.isFetching}/>
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