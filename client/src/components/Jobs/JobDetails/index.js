import React, {Component} from "react";
import JobRunLogs from "./JobRunLogs";

const GET_JOB_URL = '/api/v1/jobs/'

class Index extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isFetching: false,
            job: null
        };
    }
    render() {
        let content;
        if (this.state.job) {
            content = (
                <div>
                    <h1>{this.state.job.name }</h1>
                    <JobRunLogs job_id={this.state.job.id}/>
                </div>
            )
        }
        else {
            content = (
                <div>
                    <h1>Loading</h1>
                </div>
            )
        }
        return content;
    }

    componentDidMount() {
        this.fetchJob();
    }
    fetchJob = () => {
        this.setState({...this.state, isFetching: true});
        // here we need to append the /:id part from the Route defined in index.js
        fetch(GET_JOB_URL + this.props.match.params.id)
            .then(response => response.json())
            .then(result => {
                this.setState({job: result, isFetching: false})
            })
            .catch(e => {
                console.log(e);
                this.setState({...this.state, isFetching: false});
            });
    };
}
export default Index