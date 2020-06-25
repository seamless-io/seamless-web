import React, {Component} from "react";

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
        return (
            <div>
                <h1>{this.state.job ? this.state.job.name : 'Loading...'}</h1>
            </div>
        )
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