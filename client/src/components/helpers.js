export function getClassNameFromStatus(status) {
    switch (status) {
        case "NEW": return "JobStatus JobStatusNew";
        case "OK": return "JobStatus JobStatusOk";
        case "FAILED": return "JobStatus JobStatusFailed";
        case "EXECUTING": return "JobStatus JobStatusExecuting";
    }
}