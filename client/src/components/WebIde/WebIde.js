import React, { useState, useEffect } from 'react';

import { Row, Col } from 'react-bootstrap';

import { getJobFolderStructure, getFileContent } from '../../api';
import CodeEditor from './CodeEditor';
import FolderTree from './FolderTree';
import Notification from '../Notification/Notification';

import './style.css';

const WebIde = ({ jobId }) => {
  const [showNotification, setShowNotification] = useState(false);
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');
  const [folderStructure, setFolderStructure] = useState('');
  const [fileContent, setFileContent] = useState('');
  const [currentFile, setCurrentFile] = useState('');
  const [fileExtension, setFileExtension] = useState('');

  const displayNotification = (show, title, body, alterType) => {
    setShowNotification(show);
    setNotificationTitle(title);
    setNotificationBody(body);
    setNotificationAlertType(alterType);
  };

  const closeNotification = () => {
    setShowNotification(false);
  };

  useEffect(() => {
    getJobFolderStructure(jobId)
      .then(payload => {
        setFolderStructure(payload);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to get the folder structure :(',
          'danger'
        );
      });
  }, []);

  const showFileContent = ({ name, filePath }) => {
    setFileExtension(name.split('.')[1]);
    setCurrentFile(name);
    getFileContent(jobId, name, filePath)
      .then(payload => {
        setFileContent(payload);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to get the file content :(',
          'danger'
        );
      });
  };

  return (
    <>
      <Row className="smls-job-main-info">
        <Col
          sm={4}
          className="smls-job-main-info-section"
          style={{ borderRight: '2px solid #ebedf0' }}
        >
          <Row>
            <Col>
              <div className="smls-job-info-section-col">
                <h5>Project Tree</h5>
              </div>
            </Col>
          </Row>
          <FolderTree
            data={folderStructure}
            showFileContent={showFileContent}
          />
        </Col>
        <Col sm={8} className="smls-job-main-info-section">
          <Row>
            <Col sm={12}>
              <div className="smls-job-executiontimeline-logs-header">
                <h5>{currentFile}</h5>
              </div>
            </Col>
            <Col sm={12}>
              <CodeEditor
                fileContent={fileContent}
                fileExtension={fileExtension}
              />
            </Col>
          </Row>
        </Col>
      </Row>
      <Notification
        show={showNotification}
        closeNotification={closeNotification}
        title={notificationTitle}
        body={notificationBody}
        alertType={notificationAlertType}
      />
    </>
  );
};

export default WebIde;
