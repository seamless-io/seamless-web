import React, { useEffect, useState } from "react";
import {
    Link
} from "react-router-dom";
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';

import { getApiKey } from '../../api';

function statusFormat(fieldValue) {
    switch (fieldValue) {
        case 'New': return 'text-info';
        case 'Ok': return 'text-success';
        case 'Failed': return 'text-danger';
        case 'Executing': return 'text-warning';
        default: return 'text-white';
    }
}

function nameFormat(cell, row) {
    return (<Link to={"/jobs/" + row.id}>{cell}</Link>);
}

const JobsTable = (props) => {
    const [apiKey, setApiKey] = useState('');

    useEffect(() => {
      getApiKey()
        .then(payload => {
          setApiKey(payload.api_key)
        })
        .catch(payload => {
          alert(payload.message)
        });
    }, []);
    return (
        <div>
            <div className="row">
                <div className="col-md-12">
                    Api key: {apiKey}
                </div>
            </div>
            <BootstrapTable data={props.data} striped hover condensed>
                <TableHeaderColumn dataField='id' isKey hidden />
                <TableHeaderColumn dataField='name' dataFormat={nameFormat}>Name</TableHeaderColumn>
                <TableHeaderColumn dataField='schedule'>Schedule</TableHeaderColumn>
                <TableHeaderColumn dataField='status' columnClassName={ statusFormat }>Status</TableHeaderColumn>
            </BootstrapTable>
            <p>{props.isFetching ? 'Fetching jobs...' : ''}</p>
        </div>
    )
};
export default JobsTable