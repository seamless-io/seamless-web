import React from "react";
import {triggerJobRun} from "../../api";

function JobRunButton(props) {
    return (
        <div>
            {props.job_status === 'EXECUTING'
                ? <div className="JobExecutionSpinner"/>
                : <button className="ControlButton" onClick={() =>
                    triggerJobRun(props.job_id)}>
                    <span> Run Now </span>
                </button>
            }
        </div>
    )
}

export default JobRunButton