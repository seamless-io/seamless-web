export function getClassNameFromStatus(status) {
    switch (status) {
        case "New": return "JobStatus JobStatusNew";
        case "Ok": return "JobStatus JobStatusOk";
        case "Failed": return "JobStatus JobStatusFailed";
        case "Executing": return "JobStatus JobStatusExecuting";
    }
}