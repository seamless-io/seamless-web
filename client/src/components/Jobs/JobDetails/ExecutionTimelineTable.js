import React from "react";
import Moment from 'react-moment';
import Table from '../../table'

import { triggerJobRun } from '../../../api';
import {getClassNameFromStatus} from '../../helpers'


function ExecutionTimelineTable(props) {
    const columns = React.useMemo(
        () => [
            {
                accessor: 'created_at',
                Cell : cell =>{
                    return <Moment format="LL LTS">{cell.value}</Moment>
                }
            },
            {
                accessor: 'status',
                Cell: cell => (
                    <p className={getClassNameFromStatus(cell.value)}>{cell.value}</p>
                )
            },
        ],
        []
    )

    return (
        <Table columns={columns}
               data={props.data}
               classname="ExecutionTimelineTable"/>
    )
}

export default ExecutionTimelineTable
