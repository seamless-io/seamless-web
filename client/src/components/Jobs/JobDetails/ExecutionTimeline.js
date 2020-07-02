import React from "react";
import Moment from 'react-moment';
import Table from '../../table'

import {getClassNameFromStatus} from '../../helpers'


const ExecutionTimeline = (props) => {

    return (
        <div className="ExecutionTimeline">
            <div>
                {
                    props.data.map(function(run, i) {
                    return (
                        <div className={"JobExecutionTimelineItem" +
                        (props.selected_job_run_id === run.id ? " JobExecutionTimelineItemActive" : "")}
                             key={run.id} onClick={(row) => props.handleRowClick(run)}>
                            <div className="JobExecutionTimestampContainer">
                                <p className="primaryText">
                                    <Moment format="LL LTS" className="JobRunTimestamp">{run.created_at}</Moment>
                                </p>
                            </div>
                            <div className="JobStatusContainer">
                                <p className={getClassNameFromStatus(run.status)}>{run.status}</p>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
};
export default ExecutionTimeline
