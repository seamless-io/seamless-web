import React, { useState, useEffect } from 'react';

import { Row, Col, Spinner } from 'react-bootstrap';

import { getJobFolderStructure, getFileContent } from '../../api';
import CodeEditor from './CodeEditor';
import MemorizedTree from './FolderTree';
import Notification from '../Notification/Notification';

import './style.css';

const WebIde = ({ id, file_type, readOnly, setUnsavedChangesFlag }) => {
  const [showNotification, setShowNotification] = useState(false);
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');
  const [folderStructure, setFolderStructure] = useState('');
  const [fileContent, setFileContent] = useState('');
  const [currentFile, setCurrentFile] = useState('');
  const [fileExtension, setFileExtension] = useState('');
  const [loadingFolderTree, setLoadingFolderTree] = useState(false);
  const [loadingCodeEditor, setLoadingCodeEditor] = useState(false);
  const [currentFilePath, setCurrentFilePath] = useState('');

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
    setLoadingFolderTree(true);
    getJobFolderStructure(id, file_type)
      .then(payload => {
        setFolderStructure(payload);
        setLoadingFolderTree(false);
      })
      .catch(() => {
        setLoadingFolderTree(false);
        displayNotification(
          true,
          'Ooops!',
          'Unable to get the folder structure :(',
          'danger'
        );
      });
  }, []);

  const defineFileExtension = fileName => {
    if (fileName.includes('Dockerfile')) {
      return 'dockerfile';
    }

    return fileName.split('.')[1];
  };

  const showFileContent = ({ name, filePath }) => {
    setLoadingCodeEditor(true);
    setFileExtension(defineFileExtension(name));
    setCurrentFile(name);
    getFileContent(id, file_type, filePath)
      .then(payload => {
        setFileContent(payload);
        setLoadingCodeEditor(false);
        setCurrentFilePath(filePath);
      })
      .catch(() => {
        setLoadingCodeEditor(false);
        displayNotification(
          true,
          'Ooops!',
          'Unable to get the file content :(',
          'danger'
        );
      });
  };

  const renderFolderTree = () => {
    if (loadingFolderTree) {
      return (
        <div className="smls-web-ide-spinner-container">
          <Spinner animation="border" role="status" />
        </div>
      );
    }

    return (
      <MemorizedTree data={folderStructure} showFileContent={showFileContent} />
    );
  };

  const renderCodeEditor = () => {
    if (loadingCodeEditor) {
      return (
        <div className="smls-web-ide-spinner-container">
          <Spinner animation="border" role="status" />
        </div>
      );
    }

    if (currentFile) {
      return (
        <Col sm={12}>
          <Row>
            <Col>
              <CodeEditor
                fileContent={fileContent}
                fileExtension={fileExtension}
                readOnly={readOnly}
                id={id}
                filePath={currentFilePath}
                setUnsavedChangesFlag={setUnsavedChangesFlag}
              />
            </Col>
          </Row>
        </Col>
      );
    }

    return (
      <div className="smls-job-logs-initial-screen-container">
        Select a file from the left sidebar to view the content.
      </div>
    );
  };

  return (
    <>
      <Row className="smls-job-main-info" style={{ marginTop: '0px' }}>
        <Col
          sm={3}
          className="smls-job-main-info-section"
          style={{ borderRight: '1px solid #ebedf0' }}
        >
          <Row>
            <Col>
              <div className="smls-job-info-section-col">
                <h5 className="smls-web-ide-header">Project structure</h5>
              </div>
            </Col>
          </Row>
          {renderFolderTree()}
        </Col>
        <Col sm={9} className="smls-job-main-info-section">
          <Row>
            <Col sm={12}>
              <div className="smls-job-executiontimeline-logs-header">
                <h5 className="smls-web-ide-header">{currentFile}</h5>
                <span className="smls-web-ide-header-read-only">
                  {(currentFile && readOnly) ? 'Read only' : ''}
                </span>
              </div>
            </Col>
            {renderCodeEditor()}
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
