import React from "react";
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';

function statusFormat(fieldValue, row, rowIdx, colIdx) {
    switch (fieldValue) {
        case 'New': return 'text-info';
        case 'Ok': return 'text-success';
        case 'Failed': return 'text-danger';
        case 'Executing': return 'text-warning';
        default: return 'text-white';
    }
}


const JobsTable = (props) => {
    return (
        <div>
            <BootstrapTable data={props.data} striped hover condensed>
                <TableHeaderColumn dataField='id' isKey hidden />
                <TableHeaderColumn dataField='name'>Name</TableHeaderColumn>
                <TableHeaderColumn dataField='schedule'>Schedule</TableHeaderColumn>
                <TableHeaderColumn dataField='status' columnClassName={ statusFormat }>Status</TableHeaderColumn>
            </BootstrapTable>
            <p>{props.isFetching ? 'Fetching jobs...' : ''}</p>
        </div>
    )
};
export default JobsTable