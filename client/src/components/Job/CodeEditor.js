import React, { useState } from 'react';

import { AiOutlineFile, AiOutlineFolder } from 'react-icons/ai';
import { DiPython } from 'react-icons/di';

const FILE_ICONS = {
  py: <DiPython />,
};

const File = ({ name }) => {
  let ext = name.split('.')[1];

  return (
    <StyledFile>
      {/* render the extension or fallback to generic file icon  */}
      {FILE_ICONS[ext] || <AiOutlineFile />}
      <span>{name}</span>
    </StyledFile>
  );
};

const Folder = ({ name, children }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleToggle = e => {
    e.preventDefault();
    setIsOpen(!isOpen);
  };

  return (
    <StyledFolder>
      <div className="folder--label" onClick={handleToggle}>
        <AiOutlineFolder />
        <span>{name}</span>
      </div>
      <Collapsible isOpen={isOpen}>{children}</Collapsible>
    </StyledFolder>
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
          {/* Call the <TreeRecursive /> component with the current item.childrens */}
          <TreeRecursive data={item.childrens} />
        </Folder>
      );
    }
  });
};

const Tree = ({ data, children }) => {
  const isImparative = data && !children;

  return (
    <StyledTree>
      {isImparative ? <TreeRecursive data={data} /> : children}
    </StyledTree>
  );
};

Tree.File = File;
Tree.Folder = Folder;

export default Tree;
