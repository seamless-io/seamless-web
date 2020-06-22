import axios from 'axios';

export const logInUser = async (email, password, remember) => {
  let response = await axios.post(
    '/auth/login', {
      email,
      password,
      remember
    }
  );
  return response.data;
};
