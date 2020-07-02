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
                Cell: cell => {
                    let row = cell.cell.row.original;
                    let schedule_exists = row.schedule_is_active !== 'None';
                    let schedule_is_active = row.schedule_is_active === 'True';
                    return (
                    <div>
                        <label className="switch">
                            <input type="checkbox"
                                   checked={schedule_exists && schedule_is_active}
                                   onChange={() => props.onScheduleSwitch(row, schedule_exists, schedule_is_active)}/>
                            <span className="slider round"/>
                        </label>
                        <p className={schedule_is_active ? "secondaryText" : "secondaryText inactiveText"}>
                            {schedule_exists ? cell.value : "Not scheduled"}
                        </p>
                    </div>
                    )
                }
            },
            {
                Header: 'STATUS',
                accessor: 'status',
                Cell: cell => (
                    <div className="JobStatusContainer">
                        <p className={getClassNameFromStatus(cell.value)}>{cell.value}</p>
                    </div>
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
