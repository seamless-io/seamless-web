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
  let response = await axios.put('/api/v1/jobs/' + job_id, data);
  return response.data;
};

export const triggerJobRun = async job_id => {
  let response = await axios.post('/api/v1/jobs/' + job_id + '/run');
  return response.data;
};

export const getJobRuns = async job_id => {
  let response = await axios.get('/api/v1/jobs/' + job_id + '/runs');
  return response.data;
};

export const getJobRunLogs = async (job_id, job_run_id) => {
  let response = await axios.get(
    '/api/v1/jobs/' + job_id + '/runs/' + job_run_id + '/logs'
  );
  return response.data;
};

export const enableJobSchedule = async (job_id) => {
  let response = await axios.put(
    '/api/v1/jobs/' + job_id + '/enable'
  );
  return response.data
};

export const disableJobSchedule = async (job_id) => {
  let response = await axios.put(
    '/api/v1/jobs/' + job_id + '/disable'
  );
  return response.data
};
