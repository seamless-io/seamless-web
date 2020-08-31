import React from 'react';

import { UnControlled as CodeMirror } from 'react-codemirror2';

require('codemirror/lib/codemirror.css');
require('codemirror/theme/neo.css');
require('codemirror/mode/python/python.js');
require('codemirror/mode/javascript/javascript.js');
require('codemirror/mode/htmlmixed/htmlmixed.js');
require('codemirror/mode/markdown/markdown.js');
require('codemirror/mode/css/css.js');
require('codemirror/mode/dockerfile/dockerfile.js');

const FILE_MODE = {
  py: 'python',
  js: 'javascript',
  html: 'htmlmixed',
  md: 'markdown',
  css: 'css',
  dockerfile: 'dockerfile',
};

const CodeEditor = ({ fileContent, fileExtension }) => {
  return (
    <>
      {
        <CodeMirror
          className="smls-code-editor-window"
          value={fileContent}
          options={{
            mode: FILE_MODE[fileExtension],
            theme: 'neo',
            lineNumbers: true,
            readOnly: true,
          }}
        />
      }
    </>
  );
};

export default CodeEditor;
