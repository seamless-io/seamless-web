import React from 'react';

import { Card, OverlayTrigger, Tooltip, Col } from 'react-bootstrap';
import { AiOutlineCode, AiOutlineFileAdd, AiOutlineRead } from 'react-icons/ai';

import icons from '../../images/template_tags/*.svg';

import './style.css';

const Template = ({
  id,
  name,
  long_description_url,
  short_description,
  tags,
  openIde,
  useTemplate,
}) => {
  var templateTags = tags.split(',');
  return (
    <Col sm={4} style={{ marginBottom: '20px' }}>
      <div className="smls-templates-card-container">
        <div className="smls-templates-card-container-inner">
          <Card className="smls-templates-card">
            <Card.Body style={{ height: '240px' }}>
              <div style={{ height: '25%' }}>
                <Card.Title className="smls-templates-title">{name}</Card.Title>
              </div>
              <div
                className="smls-templates-card-body-div"
                style={{ height: '50%' }}
              >
                <Card.Text className="smls-templates-short-description">
                  {short_description}
                </Card.Text>
              </div>
              <div
                className="smls-templates-card-body-div"
                style={{ height: '25%' }}
              >
                <Card.Text>
                  {templateTags.map(tag => (
                    <img
                      key={tag}
                      src={icons[tag]}
                      height={28}
                      style={{ marginRight: '15px' }}
                    ></img>
                  ))}
                </Card.Text>
              </div>
            </Card.Body>
          </Card>
        </div>
        <div className="smls-templates-card-overlay">
          <div className="smls-templates-card-overlay-inner">
            <Card className="smls-templates-card">
              <Card.Body style={{ height: '240px' }}>
                <div>
                  <Card.Title className="smls-templates-title">
                    {name}
                  </Card.Title>
                </div>
                <div
                  style={{
                    height: '75%',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <button
                    className="smls-templates-card-button show-code"
                    data-template-id={id}
                    data-template-name={name}
                    onClick={openIde}
                  >
                    <AiOutlineCode
                      size={20}
                      style={{
                        color: '#000',
                        pointerEvents: 'none',
                        marginRight: '3px',
                      }}
                    />{' '}
                    <span className="smls-temaplates-card-button-text">
                      Show code
                    </span>
                  </button>
                  <button
                    className="smls-templates-card-button use-template"
                    data-template-id={id}
                    onClick={useTemplate}
                  >
                    <AiOutlineFileAdd
                      size={20}
                      style={{
                        color: '#fff',
                        pointerEvents: 'none',
                        marginRight: '3px',
                      }}
                    />{' '}
                    <span
                      className="smls-temaplates-card-button-text"
                      style={{ color: '#fff' }}
                    >
                      Use
                    </span>
                  </button>
                  <button
                    className="smls-templates-card-button how-to-use"
                    onClick={() => window.open(long_description_url, '_blank')}
                  >
                    <AiOutlineRead
                      size={20}
                      style={{ color: '#000', marginRight: '3px' }}
                    />{' '}
                    <span className="smls-temaplates-card-button-text">
                      Guide
                    </span>
                  </button>
                </div>
              </Card.Body>
            </Card>
          </div>
        </div>
      </div>
    </Col>
  );
};

export default Template;
