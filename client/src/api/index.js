import axios from 'axios';

export const getApiKey = async () => {
  let response = await axios.get('/api/v1/api-key');
  return response.data;
};
