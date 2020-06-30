import React, {Component} from "react";
import { getJobRunLogs } from '../../../api';

class JobRunLogs extends Component {
    constructor(props) {
        super(props);
        this.state = {
            job_id: props.job_id,
            isFetching: true,
            logs: "Fetching logs..."
        };
    }
    render() {
        return (
            <div>
                <button className="btn btn-primary pull-right" onClick={this.fetchLogs}>
                    <span className="glyphicon glyphicon-refresh" /> Refresh
                </button>
                <p>{this.state.logs ? this.state.logs : ''}</p>
            </div>
        )
    }

    componentDidMount() {
        this.fetchLogs()
    }

    fetchLogs = () => {
        this.setState({
            isFetching: true,
            logs: "Fetching logs..."
        });
        getJobRunLogs(this.state.job_id)
            .then(res => {
                console.log(res)
                var messages = res.map(function(item) {
                    return item['message'];
                });
                console.log(messages.join(''));
                this.setState({
                    isFetching: false,
                    logs: messages.join('')
                });
            })
            .catch (err => console.error(err))
    }
}
export default JobRunLogs