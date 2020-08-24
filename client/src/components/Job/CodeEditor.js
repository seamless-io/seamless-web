import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

import styled from 'styled-components';
import { Row, Col } from 'react-bootstrap';
import { AiOutlineFile, AiOutlineFolder } from 'react-icons/ai';
import { DiPython } from 'react-icons/di';

import { getJobFolderStructure } from '../../api';

const FILE_ICONS = {
  py: <DiPython />,
};

const CodeEditor = () => {
  const job = useParams();
  const [showNotification, setShowNotification] = useState(false);
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');
  const [folderStructure, setFolderStructure] = useState('');

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
    getJobFolderStructure(job.id)
      .then(payload => {
        console.log(payload);
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

  const File = ({ name }) => {
    let ext = name.split('.')[1];

    return (
      <div className="smls-code-editor-styled-file">
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
        return <File name={item.name} />;
      }
      // if its a folder render <Folder />
      if (item.type === 'folder') {
        return (
          <Folder name={item.name}>
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
      <Row>
        <Col sm={4}>
          <Tree data={folderStructure} />
        </Col>
        <Col sm={8}>File content</Col>
      </Row>
      {/* <Notification
        show={showNotification}
        closeNotification={closeNotification}
        title={notificationTitle}
        body={notificationBody}
        alertType={notificationAlertType}
      /> */}
    </>
  );
};

export default CodeEditor;
