import axios from 'axios';

export const getUserInfo = async () => {
  let response = await axios.get('/api/v1/users');
  return response.data;
};
