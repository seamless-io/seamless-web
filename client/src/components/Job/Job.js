import React, { useState, useEffect } from 'react';
import { useParams, useHistory } from 'react-router-dom';

import { Row, Col, Spinner, Modal, FormControl } from 'react-bootstrap';
import Toggle from 'react-toggle';
import moment from 'moment';
import {
  AiOutlineCode,
  AiOutlineSetting,
  AiOutlineDelete,
  AiOutlineDownload,
  AiOutlineClockCircle,
  AiOutlineEdit,
  AiOutlineCheck
} from 'react-icons/ai';

import { isValidCron } from 'cron-validator'

import { socket } from '../../socket';
import {
  getJob,
  deleteJob,
  triggerJobRun,
  enableJobSchedule,
  updateJobSchedule,
  getLastExecutions,
  getNextJobExecution,
  getJobRunLogs,
  getJobParameters,
  createJobParameter,
  deleteJobParameter,
  updateJobParameter,
} from '../../api';
import ExecutionTimeline from './ExecutionTimeline';
import WebIde from '../WebIde/WebIde';
import Parameters from '../Parameters/Parameters';
import Notification from '../Notification/Notification';

import './style.css';
import '../Jobs/toggle.css';

const Job = () => {
  const history = useHistory();
  const job = useParams();
  const downloadJobLink = `/api/v1/jobs/${job.id}/code`;
  const [name, setName] = useState('');
  const [schedule, setSchedule] = useState('');
  const [isScheduleOn, setIsScheduleOn] = useState(false);
  const [isToggleDisabled, setIsToggleDisabled] = useState(true);
  const [loading, setLoading] = useState(true);
  const [statusValue, setStatusValue] = useState(null);
  const [lastFiveExecutions, setLastFiveExecutions] = useState([]);
  const [loadingExecutionTimeLine, setLoadingExecutionTimeLine] = useState(
    true
  );
  const [nextExecution, setNextExecution] = useState('');
  const [updatedAt, setUpdatedAt] = useState('');
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [activeItem, setActiveItem] = useState(null);
  const [loadingStreamingLogs, setLoadingStreamingLogs] = useState(false);
  const [loadingToggleSwitch, setLoadingToggleSwitch] = useState(false);
  const [streamingLogs, setStreamingLogs] = useState([]);
  const [historyLogs, setHistoryLogs] = useState([]);
  const [statusRun, setStatusRun] = useState('');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationBody, setNotificationBody] = useState('');
  const [notificationAlertType, setNotificationAlertType] = useState('');
  const [showCode, setShowCode] = useState(false);
  const [showParams, setShowParams] = useState(false);
  const [jobParameters, setJobParameters] = useState([]);
  const [paramKey, setParamKey] = useState('');
  const [paramValue, setParamValue] = useState('');
  const [showEditParam, setShowEditParam] = useState(false);
  const [editedParamKey, setEditedParamKey] = useState('');
  const [editedParamValue, setEditedParamValue] = useState('');
  const [editedParamId, setEditedParamId] = useState('');
  const [borderColor, setBorderColor] = useState('#ced4da');
  const [loadingJobParams, setLoadingJobParams] = useState(false);
  const [showFaqParams, setShowFaqParams] = useState(false);
  const [isTemplate, setIsTemplate] = useState(false);
  const [alert, setAlert] = useState(false);
  const [runButtonDisabled, setRunButtonDisabled] = useState(false);
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [showCronEditor, setShowCronEditor] = useState(false);
  const [cron, setCron] = useState('');
  const [editedCron, setEditedCron] = useState('');

  const displayNotification = (show, title, body, alterType) => {
    setShowNotification(show);
    setNotificationTitle(title);
    setNotificationBody(body);
    setNotificationAlertType(alterType);
  };

  const closeNotification = () => {
    setShowNotification(false);
  };

  const updateJobStatus = jobRunning => {
    if (jobRunning.job_id === job.id) {
      setActiveItem(Number(jobRunning.job_run_id));
      setStatusValue(jobRunning.status);
      setLoadingStreamingLogs(jobRunning.status === 'EXECUTING');
    }
  };

  const updateJobLogs = jobLogLine => {
    if (jobLogLine.job_id === job.id) {
      setStreamingLogs(jobLogs => [...jobLogs, jobLogLine]);
    }
  };

  useEffect(() => {
    socket.on('status', jobRunning => updateJobStatus(jobRunning));
    socket.on('logs', jobLogLine => updateJobLogs(jobLogLine));
  }, []);

  const handleToggleSwitch = e => {
    setLoadingToggleSwitch(true);
    setIsScheduleOn(e.target.checked);
    enableJobSchedule(job.id, e.target.checked)
      .then(() => {
        setLoadingToggleSwitch(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to toggle the switch :(',
          'danger'
        );
      });
  };

  const loadToggleSwitch = () => {
    if (loadingToggleSwitch) {
      return (
        <div className="smls-job-toggle-switch-container">
          <Spinner
            animation="border"
            role="status"
            size="sm"
            style={{ marginBottom: '8px' }}
          />
        </div>
      );
    }
  };

  const isParameteresConfigured = (template, parameters) => {
    if (
      template &&
      parameters.filter(param => param.value === 'None').length !== 0
    ) {
      setAlert(true);
      setRunButtonDisabled(true);
      setIsToggleDisabled(true);
    } else {
      setAlert(false);
      setRunButtonDisabled(false);
      setIsToggleDisabled(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    getJob(job.id)
      .then(payload => {
        setName(payload.name);
        setStatusValue(payload.status);
        setUpdatedAt(
          moment.utc(payload.updated_at).format('MMM DD, YYYY, HH:mm')
        );
        setIsScheduleOn(payload.schedule_is_active === 'True');
        setIsToggleDisabled(payload.aws_cron === 'None');
        setSchedule(
          payload.human_cron === 'None' ? 'Not scheduled' : payload.human_cron
        );
        setCron(payload.cron);
        setIsTemplate(payload.job_template_id !== 'None');

        getJobParameters(job.id)
          .then(parameters => {
            setJobParameters(parameters);
            isParameteresConfigured(
              payload.job_template_id !== 'None',
              parameters
            );
          })
          .catch(() => {
            displayNotification(
              true,
              'Ooops!',
              'Unable to fetch job parameters :(',
              'danger'
            );
          });

        setLoading(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          "Unable to fetch job's details :(",
          'danger'
        );
      });
  }, []);

  useEffect(() => {
    setLoadingExecutionTimeLine(true);
    getLastExecutions(job.id)
      .then(payload => {
        setLastFiveExecutions(payload.last_executions);
        setLoadingExecutionTimeLine(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to fetch last five executions :(',
          'danger'
        );
      });
  }, [statusValue]);

  useEffect(() => {
    getNextJobExecution(job.id)
      .then(payload => {
        setNextExecution(payload.result);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to fetch the next execution details :(',
          'danger'
        );
      });
  }, []);

  const runJob = () => {
    setStreamingLogs([]);
    setStatusRun('EXECUTING');
    setLoadingExecutionTimeLine(true);
    setLoadingStreamingLogs(true);
    triggerJobRun(job.id)
      .then(() => {})
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to execute the job :(',
          'danger'
        );
      });
  };

  const runButtonContent = () => {
    if (statusValue === 'EXECUTING') {
      return (
        <Spinner
          as="span"
          animation="border"
          size="sm"
          role="status"
          aria-hidden="true"
        />
      );
    }

    return (
      <>
        <span className="smls-job-run-button-text">Run</span>
      </>
    );
  };

  const showLogs = (runId, status) => {
    setStatusRun(status);
    setLoadingStreamingLogs(status === 'EXECUTING');
    setLoadingLogs(true);
    setActiveItem(runId);
    getJobRunLogs(job.id, runId)
      .then(payload => {
        setHistoryLogs(
          payload.sort(function (a, b) {
            var dateA = new Date(a.timestamp),
              dateB = new Date(b.timestamp);
            return dateA - dateB;
          })
        );
        setLoadingLogs(false);
      })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to fetch logs :(',
          'danger'
        );
      });
  };

  const openIde = () => {
    setShowCode(true);
  };

  const closeIde = () => {
    if (unsavedChanges) {
        if (confirm('There are unsaved changes. Are you sure you don\'t want to save them?')) {
            setShowCode(false);
        }
    } else {
        setShowCode(false);
    }
  };

  const openJobParams = () => {
    setShowParams(!showParams);
  };

  const openCronEditor = () => {
    setEditedCron(cron);
    setShowCronEditor(true);
  };

  const closeCronEditor = () => {
    setShowCronEditor(false);
  };

  const cronValidationIndicator = (cronIsValid) => {
    if (cronIsValid) {
      return (
        <AiOutlineCheck style={{ color: 'green' }}/>
      );
    } else {
      return (
        <p style={{ color: 'red' }}>Invalid expression</p>
      );
    }
  };

  const updateCron = () => {
    closeCronEditor();
    setLoading(true);
    updateJobSchedule(job.id, editedCron)
      .then(payload => {
            getJob(job.id)
              .then(payload => {;
                setSchedule(
                  payload.human_cron === 'None' ? 'Not scheduled' : payload.human_cron
                );
                setCron(payload.cron);
                setLoading(false);
              })
              .catch(() => {
                displayNotification(
                  true,
                  'Ooops!',
                  "Unable to fetch job's details :(",
                  'danger'
                );
              });
          })
      .catch(() => {
        displayNotification(
          true,
          'Ooops!',
          'Unable to update the cron expression.',
          'danger'
        );
      });
  }

  const createParam = () => {
    if (!paramKey.trim() || !paramValue.trim()) {
      setBorderColor('#ff3c2e');
      return displayNotification(
        true,
        'Ooops!',
        'Parameter name and value are required.',
        'warning'
      );
    }

    setLoadingJobParams(true);
    createJobParameter(job.id, paramKey, paramValue)
      .then(() => {
        setParamKey('');
        setParamValue('');
        setBorderColor('#ced4da');
        getJobParameters(job.id)
          .then(payload => {
            setLoadingJobParams(false);
            setJobParameters(payload);
          })
          .catch(() => {
            displayNotification(
              true,
              'Ooops!',
              'Unable to fetch job parameters :(',
              'danger'
            );
          });
      })
      .catch(() => {
        setLoadingJobParams(false);
        displayNotification(
          true,
          'Ooops!',
          'Unable to created the job parameter :(',
          'danger'
        );
      });
  };

  const deleteParam = e => {
    setLoadingJobParams(true);
    deleteJobParameter(job.id, e.target.getAttribute('data-id'))
      .then(() => {
        getJobParameters(job.id)
          .then(payload => {
            setLoadingJobParams(false);
            setJobParameters(payload);
          })
          .catch(() => {
            displayNotification(
              true,
              'Ooops!',
              'Unable to fetch job parameters :(',
              'danger'
            );
          });
      })
      .catch(() => {
        setLoadingJobParams(false);
        displayNotification(
          true,
          'Ooops!',
          'Unable to delete the job parameter :(',
          'danger'
        );
      });
  };

  const editParam = e => {
    setShowParams(!showParams);
    setShowEditParam(!showEditParam);
    setEditedParamId(e.target.getAttribute('data-id'));
    setEditedParamKey(e.target.getAttribute('data-key'));
    setEditedParamValue(e.target.getAttribute('data-value'));
  };

  const hideEditParam = () => {
    setShowParams(!showParams);
    setShowEditParam(!showEditParam);
  };

  const switchParameters = () => {
    setShowFaqParams(true);
    setShowParams(false);
  };

  const closeParams = () => {
    setShowParams(!showParams);
    setShowFaqParams(false);
  };

  const closeFaqParams = () => {
    setShowFaqParams(false);
    setShowParams(true);
  };

  const updateParam = () => {
    setLoadingJobParams(true);
    updateJobParameter(job.id, editedParamId, editedParamKey, editedParamValue)
      .then(() => {
        getJobParameters(job.id)
          .then(parameters => {
            setLoadingJobParams(false);
            setJobParameters(parameters);
            isParameteresConfigured(isTemplate, parameters);
          })
          .catch(() => {
            displayNotification(
              true,
              'Ooops!',
              'Unable to fetch job parameters :(',
              'danger'
            );
          });

        setShowParams(!showParams);
        setShowEditParam(!showEditParam);
      })
      .catch(() => {
        setLoadingJobParams(false);
        displayNotification(
          true,
          'Ooops!',
          'Unable to update the job parameter :(',
          'danger'
        );
      });
  };

  const parametersAlert = () => {
    if (alert) {
      return (
        <Col sm={12} style={{ paddingLeft: '0px', paddingRight: '0px' }}>
          <div className="smls-job-parameters-alert">
            Set up parameters to be able to run this job.
          </div>
        </Col>
      );
    }
  };

  const tryToDeleteJob = () => {
    if (confirm('Are you sure you want to delete this Job?')) {
      setLoading(true);
      deleteJob(job.id)
        .then(() => {
          history.push('/');
        })
        .catch(() => {
          displayNotification(
            true,
            'Ooops!',
            'Unable to delete the job :(',
            'danger'
          );
          setLoading(false);
        });
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
      <Row className="smls-job-header">
        <Col className="smls-job-name-header" sm={5}>
          <div className="smls-job-heade-container">
            <h1 className="smls-job-name-h1">{name}</h1>
          </div>
        </Col>
        <Col className="smls-job-header-buttons-container" sm={7}>
          <div className="smls-job-header-buttons">
            <button
              className="smls-job-run-button"
              type="button"
              disabled={statusValue === 'EXECUTING' || runButtonDisabled}
              onClick={runJob}
            >
              {runButtonContent()}
            </button>
            <button
              className="smls-job-web-ide-button"
              type="button"
              onClick={openIde}
            >
              <AiOutlineCode />
              <span className="smls-job-web-ide-button-text">Edit Code</span>
            </button>
            <button
              className={
                alert
                  ? 'smls-job-web-ide-button alert-border'
                  : 'smls-job-web-ide-button'
              }
              type="button"
              onClick={openJobParams}
            >
              <AiOutlineSetting />
              <span className="smls-job-web-ide-button-text">
                Job Parameters
              </span>
            </button>
            <a href={downloadJobLink}>
              <button className="smls-job-download-code-button" type="button">
                <AiOutlineDownload />
                <span className="smls-job-download-code-button-text">
                  Download Code
                </span>
              </button>
            </a>
            <button
              className="smls-job-delete-button"
              type="button"
              onClick={tryToDeleteJob}
            >
              <AiOutlineDelete />
              <span className="smls-job-delete-button-text">Delete Job</span>
            </button>
          </div>
        </Col>
        {parametersAlert()}
      </Row>
      <Row className="smls-job-extra-info">
        <Col style={{ paddingLeft: '0px' }}>
          <div
            className="smls-job-extra-info-section"
            style={{ position: 'absolute' }}
          >
            <Toggle
              checked={isScheduleOn}
              icons={false}
              disabled={isToggleDisabled}
              onChange={handleToggleSwitch}
            />
            <span className={!isScheduleOn ? 'smls-muted' : ''}>
              {schedule} UTC
            </span>
            <AiOutlineEdit
                style={{ marginLeft: '10px', cursor: 'pointer'}}
                onClick={openCronEditor} />
          </div>
          {loadToggleSwitch()}
        </Col>
        <Col style={{ paddingRight: '0px' }}>
          <div className="smls-job-extra-info-section">
            <AiOutlineClockCircle />
            <span>{`Code updated on ${updatedAt} UTC`}</span>
          </div>
        </Col>
      </Row>
      <ExecutionTimeline
        loadingExecutionTimeLine={loadingExecutionTimeLine}
        lastFiveExecutions={lastFiveExecutions}
        nextExecution={nextExecution}
        logs={statusRun === 'EXECUTING' ? streamingLogs : historyLogs}
        showLogs={showLogs}
        loadingLogs={loadingLogs}
        activeItem={activeItem}
        loadingStreamingLogs={loadingStreamingLogs}
      />
      <Notification
        show={showNotification}
        closeNotification={closeNotification}
        title={notificationTitle}
        body={notificationBody}
        alertType={notificationAlertType}
      />

      <Modal
        show={showCode}
        onHide={() => closeIde()}
        dialogClassName="smls-web-ide-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>{name}</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ paddingTop: '0px' }}>
          <WebIde id={job.id} file_type="jobs" readOnly={false}
           setUnsavedChangesFlag={setUnsavedChanges}/>
        </Modal.Body>
      </Modal>
      <Modal
        show={showParams}
        onHide={closeParams}
        dialogClassName="smls-job-param-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>Job Parameters</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ paddingTop: '0px' }}>
          <span onClick={switchParameters} className="smls-job-params-guide">
            How to use job parameters?
          </span>
          <Parameters
            jobParameters={jobParameters}
            paramKey={paramKey}
            paramValue={paramValue}
            setKey={e => setParamKey(e.target.value)}
            setValue={e => setParamValue(e.target.value)}
            createParam={createParam}
            editParam={editParam}
            deleteParam={deleteParam}
            borderColor={borderColor}
            loadingJobParams={loadingJobParams}
          />
        </Modal.Body>
      </Modal>
      <Modal
        show={showEditParam}
        onHide={hideEditParam}
        dialogClassName="smls-job-param-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>Edit job parameter</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ paddingTop: '0px' }}>
          <Row style={{ paddingTop: '16px' }}>
            <Col sm={5}>
              <FormControl
                placeholder="Key"
                value={editedParamKey}
                onChange={e => setEditedParamKey(e.target.value.trim())}
              />
            </Col>
            <Col sm={5}>
              <FormControl
                placeholder="Value"
                value={editedParamValue}
                onChange={e => setEditedParamValue(e.target.value)}
              />
            </Col>
            <Col sm={2}>
              <button
                className="smls-job-param-save-changes"
                type="button"
                onClick={updateParam}
              >
                <span className="smls-job-param-button-text">Save changes</span>
              </button>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>
      <Modal
        show={showFaqParams}
        onHide={closeFaqParams}
        dialogClassName="smls-job-param-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>How to use job parameters?</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ paddingTop: '0px' }}>
          <div className="smls-job-params-quide-container">
            <Row style={{ paddingTop: '16px' }}>
              <Col>
                <div className="smls-guide-code-section">
                  <code className="smls-code-comment">
                    # If you are new in programming, there is a useful blog
                    about environment variables:
                    https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html
                    <br />
                    <br />
                    # Job parameters are environment variables that change the
                    way your job behaves. <br /># For example, you set up via
                    SeamlessCloud UI two parameters:
                    DB_HOST=prod-server.com:5432 and DB_PASSWORD=1234. <br />#
                    Then you can access these variables in your code:
                  </code>
                  <br />
                  <code>
                    import os <br />
                    <br />
                    DB_HOST = os.getenv('DB_HOST') <br />
                    DB_PASSWORD = os.getenv('DB_PASSWORD')
                  </code>
                  <code className="smls-code-comment">
                    <br />
                    # If you change values of variabels to
                    DB_HOST=staging-server.com:5432 and DB_PASSWORD=4321, and
                    click "Run" <br />
                    # your job will connect to your database.
                    <br />
                    <br /># For local development, it is better to use{' '}
                    <i>.env</i> file: https://pypi.org/project/python-dotenv/
                  </code>
                </div>
              </Col>
            </Row>
          </div>
        </Modal.Body>
      </Modal>
      <Modal
        show={showCronEditor}
        onHide={closeCronEditor}
        dialogClassName="smls-cron-editor-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>Edit schedule</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ paddingTop: '0px' }}>
          <Row>
            <Col>
                <p className="smls-job-params-guide">
                You can use <a href="https://crontab.guru/" target="_blank">crontab.guru</a> as a reference for CRON expressions.
                </p>
            </Col>
          </Row>
          <Row style={{ paddingTop: '16px' }}>
            <Col sm={4}>
              <FormControl
                value={editedCron}
                onChange={e => setEditedCron(e.target.value)}
              />
            </Col>
            <Col sm={4}>
            {cronValidationIndicator(isValidCron(editedCron))}
            </Col>
            <Col sm={4}>
              <button
                className="smls-job-param-save-changes"
                type="button"
                onClick={updateCron}
                disabled={isValidCron(editedCron) ? "" : "disabled"}
              >
                <span className="smls-job-param-button-text">Save changes</span>
              </button>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>
    </>
  );
};

export default Job;
