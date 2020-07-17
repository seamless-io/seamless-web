import  useEffect  from "react";
import getJobRunLogs from "../../../api";

const ExecutionTimeline  = () => {
  const [logs, setLogs] = useState('');

  // useEffect(() => {
  //   getJobRunLogs(job.id)
  // }, []);

  return (
    <Row className="smls-job-main-info">
      <Col
        sm={4}
        className="smls-job-main-info-section"
        style={{ borderRight: '2px solid #ebedf0' }}
      >
        <Row>
          <Col>
            <div className="smls-job-info-section-col">
              <h5>Execution Timeline</h5>
            </div>
          </Col>
        </Row>
        <Row>
          <Col>
            <div className="smls-job-info-section-col-scheduled">
              <div className="smls-job-info-section-col-scheduled-text">
                Devember 25, 2020, 05:08
              </div>
              <div className="smls-job-info-section-col-scheduled-badge">
                <span>scheduled</span>
              </div>
            </div>
          </Col>
        </Row>
        <Row>
          <Col>
            <div className="smls-job-info-section-col-hr">
              <hr />
            </div>
          </Col>
        </Row>
      </Col>
      <Col sm={8} className="smls-job-main-info-section">
        <Row>
          <Col sm={12}>
            <h5 className="smls-job-main-info-section-header">Logs</h5>
          </Col>
          <Col sm={12}>
            <div className="smls-job-container">logs....</div>
          </Col>
        </Row>
      </Col>
    </Row>
  )
}

export default ExecutionTimeline;
