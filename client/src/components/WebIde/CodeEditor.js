import React, { useState, useEffect } from 'react';

import { Row, Col } from 'react-bootstrap';

import { UnControlled as CodeMirror } from 'react-codemirror2';

require('codemirror/lib/codemirror.css');
require('codemirror/theme/neo.css');
require('codemirror/mode/python/python.js');
require('codemirror/mode/javascript/javascript.js');
require('codemirror/mode/htmlmixed/htmlmixed.js');
require('codemirror/mode/markdown/markdown.js');
require('codemirror/mode/css/css.js');
require('codemirror/mode/dockerfile/dockerfile.js');

import {saveCode} from '../../api';

const FILE_MODE = {
  py: 'python',
  js: 'javascript',
  html: 'htmlmixed',
  md: 'markdown',
  css: 'css',
  dockerfile: 'dockerfile',
};

const CodeEditor = ({ fileContent, fileExtension, readOnly, id, filePath, setUnsavedChangesFlag }) => {
  const [unsavedContent, setUnsavedContent] = useState('');

  const renderSaveButton = () => {
    if (!readOnly) {
        if (unsavedContent) {
          return (
              <button
                className="smls-ide-save-button"
                type="button"
                onClick={saveFile}>
                      <span className="smls-ide-save-button-text">Save</span>
              </button>
          );
        } else {
        return (
              <button
                className="smls-ide-save-button"
                type="button"
                onClick={saveFile}
                disabled="disabled">
                      <span className="smls-ide-save-button-text">Save</span>
              </button>
          );
        }
    }
  };

  const saveFile = () => {
      saveCode(id, filePath, unsavedContent)
      .then(() => {})
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to save file',
          'danger'
        );
      });
      setUnsavedChangesFlag(false);
      setUnsavedContent('');
  };

  if (FILE_MODE[fileExtension] || fileExtension === 'txt') {
    return (
      <>
        <Row>
        <Col>
          <CodeMirror
            className="smls-code-editor-window"
            value={fileContent}
            options={{
              mode: FILE_MODE[fileExtension],
              theme: 'neo',
              lineNumbers: true,
              readOnly: readOnly,
            }}
            onChange={(editor, data, value) => {
              setUnsavedContent(value);
              setUnsavedChangesFlag(true);
            }}
          />
         </Col>
         </Row>
         <Row>
         <Col>
             {renderSaveButton()}
         </Col>
         </Row>
      </>
    );
  }

  return (
    <div className="smls-job-logs-initial-screen-container">
      View is not available for this file extension.
    </div>
  );
};

export default CodeEditor;
