import React, { useState } from 'react';

import styled from 'styled-components';
import { AiOutlineFile, AiFillFolder, AiFillFolderOpen } from 'react-icons/ai';
import {
  DiPython,
  DiMarkdown,
  DiJavascript1,
  DiHtml5,
  DiCss3,
} from 'react-icons/di';

const FILE_ICONS = {
  py: <DiPython />,
  md: <DiMarkdown />,
  js: <DiJavascript1 />,
  html: <DiHtml5 />,
  css: <DiCss3 />,
};

const FolderTree = ({ data, showFileContent }) => {
  const Collapsible = styled.div`
    height: ${p => (p.isOpen ? 'auto' : '0')};
    overflow: hidden;
  `;

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

    const folderIcon = isOpen ? (
      <AiFillFolderOpen color="#016bff" />
    ) : (
      <AiFillFolder color="#016bff" />
    );

    return (
      <div className="smls-code-editor-styled-folder">
        <div className="folder--label" onClick={handleToggle}>
          {folderIcon}
          <span>{name}</span>
        </div>
        <Collapsible isOpen={isOpen}>{children}</Collapsible>
      </div>
    );
  };

  const TreeRecursive = ({ data }) => {
    return data.map(item => {
      if (item.type === 'file') {
        return <File key={item.name} name={item.name} filePath={item.path} />;
      }
      if (item.type === 'folder') {
        return (
          <Folder key={item.name} name={item.name}>
            <TreeRecursive data={item.children} />
          </Folder>
        );
      }
    });
  };

  const Tree = ({ data, children }) => {
    const isImperative = data && !children;

    return (
      <div className="smls-code-editor-styled-tree">
        {isImperative ? <TreeRecursive data={data} /> : children}
      </div>
    );
  };

  Tree.File = File;
  Tree.Folder = Folder;

  return (
    <>
      <Tree data={data} />
    </>
  );
};

export default FolderTree;
