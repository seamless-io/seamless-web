import React, { useState, useEffect } from 'react';

import styled from 'styled-components';
import { Row, Col } from 'react-bootstrap';
import { AiOutlineFile, AiOutlineFolder } from 'react-icons/ai';
import {
  DiPython,
  DiMarkdown,
  DiJavascript1,
  DiHtml5,
  DiCss3,
} from 'react-icons/di';

import { getJobFolderStructure, getFileContent } from '../../api';
import Notification from '../Notification/Notification';

const FILE_ICONS = {
  py: <DiPython />,
  md: <DiMarkdown />,
  js: <DiJavascript1 />,
  html: <DiHtml5 />,
  css: <DiCss3 />,
};

const CodeEditor = ({ jobId }) => {
  const [showNotification, setShowNotification] = useState(false);
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');
  const [folderStructure, setFolderStructure] = useState('');
  const [fileContent, setFileContent] = useState('');
  const [currentFile, setCurrentFile] = useState('');

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

  const Collapsible = styled.div`
    height: ${p => (p.isOpen ? 'auto' : '0')};
    overflow: hidden;
  `;

  const showFileContent = ({ name, filePath }) => {
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

  const File = ({ name, filePath }) => {
    let ext = name.split('.')[1];

    return (
      <div
        className="smls-code-editor-styled-file"
        onClick={() => showFileContent({ name, filePath })}
      >
        {/* render the extension or fallback to generic file icon  */}
        {FILE_ICONS[ext] || <AiOutlineFile />}
        <span>{name}</span>
      </div>
    );
  };

  const Folder = ({ name, children }) => {
    const [isOpen, setIsOpen] = useState(false);

    const handleToggle = e => {
      e.preventDefault();
      setIsOpen(!isOpen);
    };

    return (
      <div className="smls-code-editor-styled-folder">
        <div className="folder--label" onClick={handleToggle}>
          <AiOutlineFolder />
          <span>{name}</span>
        </div>
        <Collapsible isOpen={isOpen}>{children}</Collapsible>
      </div>
    );
  };

  const TreeRecursive = ({ data }) => {
    // loop through the data
    return data.map(item => {
      // if its a file render <File />
      if (item.type === 'file') {
        return <File key={item.name} name={item.name} filePath={item.path} />;
      }
      // if its a folder render <Folder />
      if (item.type === 'folder') {
        return (
          <Folder key={item.name} name={item.name}>
            {/* Call the <TreeRecursive /> component with the current item.children */}
            <TreeRecursive data={item.children} />
          </Folder>
        );
      }
    });
  };

  const Tree = ({ data, children }) => {
    const isImparative = data && !children;

    return (
      <div className="smls-code-editor-styled-tree">
        {isImparative ? <TreeRecursive data={data} /> : children}
      </div>
    );
  };

  Tree.File = File;
  Tree.Folder = Folder;

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
          <Tree data={folderStructure} />
        </Col>
        <Col sm={8} className="smls-job-main-info-section">
          <Row>
            <Col sm={12}>
              <div className="smls-job-executiontimeline-logs-header">
                <h5>{`File: ${currentFile}`}</h5>
              </div>
            </Col>
            <Col sm={12}>{fileContent}</Col>
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

export default CodeEditor;
