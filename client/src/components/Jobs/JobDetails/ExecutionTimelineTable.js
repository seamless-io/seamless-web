import React from "react";
import Moment from 'react-moment';
import Table from '../../table'

import {getClassNameFromStatus} from '../../helpers'


function ExecutionTimelineTable(props) {
    const columns = React.useMemo(
        () => [
            {
                accessor: 'created_at',
                Cell : cell =>(
                    <a onClick={(row) => props.handleRowClick(cell.row.original)}
                       className="primaryText">
                        <Moment format="LL LTS" className="JobRunTimestamp">{cell.value}
                        </Moment></a>
                )
            },
            {
                accessor: 'status',
                Cell: cell => (
                    <div className="JobStatusContainer">
                        <p className={getClassNameFromStatus(cell.value)}>{cell.value}</p>
                    </div>
                )
            },
        ],
        []
    )

    return (
        <Table columns={columns}
               data={props.data}
               no_table_header={true}
               classname="ExecutionTimelineTable"/>
    )
}

export default ExecutionTimelineTable
