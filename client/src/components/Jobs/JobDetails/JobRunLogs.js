import React from "react";
import {BootstrapTable, TableHeaderColumn} from "react-bootstrap-table";

const JobRunLogs = (props) => {
    return (
        <div>
            <button className="btn btn-primary pull-right" onClick={props.handleRefreshClick}>
                <span className="glyphicon glyphicon-refresh" /> Refresh
            </button>
            <h3>Logs</h3>
            <BootstrapTable data={props.logs} bordered={ false } scrollTop={ 'Bottom' }>
                <TableHeaderColumn dataField='id' isKey hidden />
                <TableHeaderColumn dataField='timestamp'>Time</TableHeaderColumn>
                <TableHeaderColumn dataField='message'>Message</TableHeaderColumn>
            </BootstrapTable>
            <p>{props.isFetching ? 'Fetching logs...' : ''}</p>
        </div>
    )
};
export default JobRunLogs
