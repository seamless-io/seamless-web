import io from 'socket.io-client';

export const socket = io(
  location.protocol + '//' + document.domain + ':' + location.port + '/socket'
);
