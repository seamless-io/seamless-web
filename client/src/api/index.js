import axios from 'axios';

export const getUserInfo = async () => {
  let response = await axios.get('/api/v1/user');
  return response.data;
};

export const getJobs = async () => {
  let response = await axios.get('/api/v1/jobs');
  return response.data;
};

export const getJob = async job_id => {
  let response = await axios.get(`/api/v1/jobs/${job_id}`);
  return response.data;
};

export const updateJob = async (job_id, data) => {
  let response = await axios.put(`/api/v1/jobs/${job_id}`, data);
  return response.data;
};

export const triggerJobRun = async job_id => {
  let response = await axios.post(`/api/v1/jobs/${job_id}/run`);
  return response.data;
};

export const getJobRunLogs = async (job_id, job_run_id) => {
  let response = await axios.get(
    `/api/v1/jobs/${job_id}/runs/${job_run_id}/logs`
  );
  return response.data;
};

export const getLastExecutions = async job_id => {
  let response = await axios.get(`/api/v1/jobs/${job_id}/executions`);
  return response.data;
};

export const enableJobSchedule = async (job_id, is_enabled) => {
  let response = await axios.put(
    `/api/v1/jobs/${job_id}/schedule?is_enabled=${is_enabled}`
  );
  return response.data;
};

export const getNextJobExecution = async job_id => {
  let response = await axios.get(`/api/v1/jobs/${job_id}/next_execution`);
  return response.data;
};

export const getJobFolderStructure = async job_id => {
  let response = await axios.get(`/api/v1/jobs/${job_id}/folder`);
  return response.data;
};

export const getFileContent = async (job_id, file_path) => {
  let response = await axios.get(
    `/api/v1/jobs/${job_id}/file?file_path=${file_path}`
  );
  return response.data;
};

export const getJobParameters = async job_id => {
  let response = await axios.get(`/api/v1/jobs/${job_id}/parameters`);
  return response.data;
};

export const createJobParameter = async (job_id, key, value) => {
  let response = await axios.post(`/api/v1/jobs/${job_id}/parameters`, {
    key: key,
    value: value,
  });
  return response.data;
};

export const deleteJobParameter = async (job_id, parameter_id) => {
  let response = await axios.delete(
    `/api/v1/jobs/${job_id}/parameters/${parameter_id}`
  );
  return response.data;
};

export const updateJobParameter = async (job_id, parameter_id, key, value) => {
  let response = await axios.put(
    `/api/v1/jobs/${job_id}/parameters/${parameter_id}`,
    {
      key: key,
      value: value,
    }
  );
  return response.data;
};
