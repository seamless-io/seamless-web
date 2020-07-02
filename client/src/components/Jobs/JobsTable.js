import React from "react";
import Table from '../table'
import {useHistory} from 'react-router-dom'

import JobRunButton from "./JobRunButton";
import {getClassNameFromStatus} from '../helpers'


function JobsTable(props) {
    const history = useHistory();

    const columns = React.useMemo(
        () => [
            {
                Header: 'NAME',
                accessor: 'name',
                Cell: cell => (
                    <a onClick={() => history.push("/jobs/" + cell.row.original.id)}
                       className="primaryText">{cell.value}</a>
                )
            },
            {
                Header: 'SCHEDULE',
                accessor: 'schedule',
                Cell: cell => (
                    <div>
                        <label className="switch">
                            <input type="checkbox"/>
                            <span className="slider round"/>
                        </label>
                        <p className="secondaryText">{cell.value}</p>
                    </div>
                )
            },
            {
                Header: 'STATUS',
                accessor: 'status',
                Cell: cell => (
                    <p className={getClassNameFromStatus(cell.value)}>{cell.value}</p>
                )
            },
            {
                Header: "CONTROLS",
                accessor: "controls",
                Cell: cell => (
                    <JobRunButton job_id={cell.row.original.id}
                                  job_status={cell.row.original.status}/>
                )
            }
        ],
        []
    )

    return (
        <Table columns={columns}
               data={props.data}
               classname="JobsTable"/>
    )
}

export default JobsTable
