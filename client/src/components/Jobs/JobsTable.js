import React, { useEffect, useState } from "react";
import {
    Link
} from "react-router-dom";
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';

import { getUserInfo, triggerJobRun } from '../../api';

function statusFormat(fieldValue) {
    switch (fieldValue) {
        case 'New': return 'text-info';
        case 'Ok': return 'text-success';
        case 'Failed': return 'text-danger';
        case 'Executing': return 'text-warning';
        default: return 'text-white';
    }
}

function nameFormatter(cell, row) {
    return (
        <Link to={"/jobs/" + row.id}>{cell}</Link>
    );
}
function buttonFormatter(cell, row){
    return (
        <button className="btn btn-primary" onClick={() => triggerJobRun(row.id)}>
            <span className="glyphicon glyphicon-play-circle" /> Run
        </button>
    );
}

const JobsTable = (props) => {
    const [userInfo, setUserInfo] = useState('');

    useEffect(() => {
      getUserInfo()
        .then(payload => {
          setUserInfo(payload.api_key)
        })
        .catch(payload => {
          alert(payload.message)
        });
    }, []);
    return (
        <div>
            <div className="row">
                <div className="col-md-12">
                    Api key: {userInfo}
                </div>
            </div>
            <BootstrapTable data={props.data} striped hover condensed>
                <TableHeaderColumn dataField='id' isKey hidden />
                <TableHeaderColumn dataField='name' dataFormat={nameFormatter}>Name</TableHeaderColumn>
                <TableHeaderColumn dataField='schedule'>Schedule</TableHeaderColumn>
                <TableHeaderColumn dataField='status' columnClassName={ statusFormat }>Status</TableHeaderColumn>
                <TableHeaderColumn dataField='button' dataFormat={buttonFormatter}>Controls</TableHeaderColumn>
            </BootstrapTable>
            <p>{props.isFetching ? 'Fetching jobs...' : ''}</p>
        </div>
    )
};
export default JobsTable