import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';

import { Spinner, Modal, Row } from 'react-bootstrap';

import { getTemlaptes, addTemplate } from '../../api';
import Notification from '../Notification/Notification';
import Template from './Template';
import WebIde from '../WebIde/WebIde';

const Templates = () => {
  const history = useHistory();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');
  const [showCode, setShowCode] = useState(false);
  const [templateId, setTemplateId] = useState('');
  const [templateName, setTemplateName] = useState('');

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
    getTemlaptes()
      .then(payload => {
        setTemplates(payload);
        setLoading(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to get the list of templates :(',
          'danger'
        );
        setLoading(false);
      });
  }, []);

  const openIde = e => {
    setShowCode(!showCode);
    setTemplateId(e.target.getAttribute('data-template-id'));
    setTemplateName(e.target.getAttribute('data-template-name'));
  };

  const useTemplate = e => {
    setLoading(true);
    addTemplate(e.target.getAttribute('data-template-id'))
      .then(payload => {
        setLoading(false);
        history.push(`jobs/${payload.job_id}`);
      })
      .catch(err => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to add the template. ' + err.response['data'],
          'danger'
        );
        setLoading(false);
      });
  };

  const renderTemplates = () => {
    if (templates && templates.length > 0) {
      return templates.map(template => (
        <Template
          key={template.id}
          {...template}
          openIde={openIde}
          useTemplate={useTemplate}
        />
      ));
    }
  };

  if (loading) {
    return (
      <div className="smls-jobs-spinner-container">
        <Spinner animation="border" role="status" />
      </div>
    );
  }

  return (
    <>
      <Row style={{ paddingTop: '30px' }}>{renderTemplates()}</Row>
      <Modal
        show={showCode}
        onHide={() => setShowCode(!showCode)}
        dialogClassName="smls-web-ide-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>{templateName}</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ paddingTop: '0px' }}>
          <WebIde id={templateId} file_type="templates" />
        </Modal.Body>
      </Modal>
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

export default Templates;
