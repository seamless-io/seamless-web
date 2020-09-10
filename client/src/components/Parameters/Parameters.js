import React from 'react';
import PropTypes from 'prop-types';

import { Row, Col, FormControl, Spinner } from 'react-bootstrap';
import { AiOutlineEdit, AiOutlineClose } from 'react-icons/ai';

import './style.css';

const Parameters = ({
  jobParameters,
  paramKey,
  paramValue,
  setKey,
  setValue,
  createParam,
  editParam,
  deleteParam,
  borderColor,
  loadingJobParams,
}) => {
  if (loadingJobParams) {
    return (
      <div className="smls-job-param-loading">
        <Spinner animation="border" role="status" />
      </div>
    );
  }

  const jobParams = () => {
    if (typeof jobParameters !== 'undefined' && jobParameters.length === 0) {
      return (
        <div className="smls-job-no-params">
          <Row>
            <Col>There are no parameters yet.</Col>
          </Row>
        </div>
      );
    }

    const renderJobParams = jobParameters.map(param => (
      <Row key={param.id} style={{ paddingTop: '16px' }}>
        <Col sm={5}>
          <FormControl placeholder="Key" value={param.key} readOnly />
        </Col>
        <Col sm={5}>
          <FormControl placeholder="Value" value={param.value} readOnly />
        </Col>
        <Col sm={2} className="smls-job-param-buttons-containenr">
          <span
            className="smls-job-param-edit-button"
            onClick={editParam}
            data-id={param.id}
            data-key={param.key}
            data-value={param.value}
          >
            <AiOutlineEdit style={{ pointerEvents: 'none' }} />
          </span>
          <span
            onClick={deleteParam}
            data-id={param.id}
            className="smls-job-param-delete-button"
          >
            <AiOutlineClose style={{ pointerEvents: 'none' }} />
          </span>
        </Col>
      </Row>
    ));

    return <>{renderJobParams}</>;
  };

  const addNewParam = () => {
    return (
      <Row>
        <Col sm={5}>
          <FormControl
            placeholder="Key"
            value={paramKey}
            onChange={setKey}
            style={{ border: `1px solid ${borderColor}` }}
          />
        </Col>
        <Col sm={5}>
          <FormControl
            placeholder="Value"
            value={paramValue}
            onChange={setValue}
            style={{ border: `1px solid ${borderColor}` }}
          />
        </Col>
        <Col sm={2}>
          <button
            className="smls-job-param-create"
            type="button"
            onClick={createParam}
          >
            <span className="smls-job-param-button-text">Add</span>
          </button>
        </Col>
      </Row>
    );
  };

  return (
    <>
      <div className="smls-job-params-container">{jobParams()}</div>
      <hr />
      {addNewParam()}
    </>
  );
};

export default Parameters;

Parameters.propTypes = {
  jobParameters: PropTypes.array,
  paramKey: PropTypes.string,
  paramValue: PropTypes.string,
  setKey: PropTypes.func,
  setValue: PropTypes.func,
  createParam: PropTypes.func,
  editParam: PropTypes.func,
  deleteParam: PropTypes.func,
  borderColor: PropTypes.string,
  loadingJobParams: PropTypes.bool,
};

Parameters.defaultProps = {
  jobParameters: [],
  paramKey: '',
  paramValue: '',
  setKey: null,
  setValue: null,
  createParam: null,
  editParam: null,
  deleteParam: null,
  borderColor: 'ced4da',
  loadingJobParams: false,
};
