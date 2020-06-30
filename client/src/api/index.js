import axios from 'axios';

export const getUserInfo = async () => {
  let response = await axios.get('/api/v1/user');
  return response.data;
};

export const triggerJobRun = async (job_id) => {
  let response = await axios.post('/api/v1/jobs/' + job_id + '/run');
  return response.data;
};

export const getJobRunLogs = async (job_id) => {
  let response = await axios.get('/api/v1/jobs/' + job_id + '/logs');
  return response.data;
};
