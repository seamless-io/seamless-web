import React from "react";
import Moment from "react-moment";

const JobRunLogs = (props) => {
    return (
        <div className="JobRunLogs">
            <button className="ControlButton" onClick={props.handleRefreshClick}>
                <span> Refresh </span>
            </button>
            <div>
                {props.logs.map(function(log_record, i){
                    return <p className="JobRunLogRecord" key={i}>
                        <Moment format="LL LTS">{log_record.timestamp}</Moment> : {log_record.message} </p>;
                })}
            </div>
        </div>
    )
};
export default JobRunLogs
