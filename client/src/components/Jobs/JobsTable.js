import React from "react";
import Table from '../table'
import {useHistory} from 'react-router-dom'

import { triggerJobRun } from '../../api';

function getClassNameFromStatus(status) {
    switch (status) {
        case "New": return "JobStatus JobStatusNew";
        case "Ok": return "JobStatus JobStatusOk";
        case "Failed": return "JobStatus JobStatusFailed";
        case "Executing": return "JobStatus JobStatusExecuting";
    }
}

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
                    <button className="ControlButton" onClick={() =>
                        triggerJobRun(cell.row.original.id)}>
                        <span> Run Now </span>
                    </button>
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
