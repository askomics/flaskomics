import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button, InputGroupAddon, Input, InputGroup, Row, Col, ListGroup, ListGroupItem, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import AskoContext from '../../components/context'
import UploadGalaxyForm from '../upload/uploadgalaxyform'


export default class Ask extends Component {
  static contextType = AskoContext
  constructor (props) {
    super(props)
    this.state = {
      waiting: true,
      error: false,
      errorMessage: null,
      startpoints: [],
      selected: null,
      startSession: false,
      publicQueries: [],
      modalGalaxy: false
    }
    this.cancelRequest
    this.handleClick = this.handleClick.bind(this)
    this.handleStart = this.handleStart.bind(this)
    this.handleFilter = this.handleFilter.bind(this)
    this.handleClickPublicQuery = this.handleClickPublicQuery.bind(this)
    this.toggleModalGalaxy = this.toggleModalGalaxy.bind(this)
  }

  componentDidMount () {

    if (!this.props.waitForStart) {
      let requestUrl = '/api/query/startpoints'
      axios.get(requestUrl, {baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
          console.log(requestUrl, response.data)
          this.setState({
            waiting: false,
            startpoints: response.data.startpoints.map(startpoint => new Object({
              graphs: startpoint.graphs,
              entity: startpoint.entity,
              entity_label: startpoint.entity_label,
              public: startpoint.public,
              private: startpoint.private,
              hidden: false,
              selected: false
            })),
            publicQueries: response.data.publicQueries,
            startSessionWithExemple: false
          })
        })
        .catch(error => {
          console.log(error, error.response.data.errorMessage)
          this.setState({
            waiting: false,
            error: true,
            errorMessage: error.response.data.errorMessage,
            status: error.response.status
          })
        })
    }
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  handleClick (event) {
    this.setState({
      selected: event.target.id
    })
  }

  handleStart (event) {
    console.log('Start session with ' + this.state.selected)
    this.setState({
      startSession: true
    })
  }

  handleClickPublicQuery (event) {
    // request api to get a preview of file
    let requestUrl = '/api/results/graphstate'
    let data = { fileId: event.target.id }
    axios.post(requestUrl, data, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        // set state of resultsPreview
        this.setState({
          startSessionWithExemple: true,
          graphState: response.data.graphState
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          waiting: false
        })
      })
  }

  toggleModalGalaxy (event) {
    this.setState({
      modalGalaxy: !this.state.modalGalaxy
    })
  }

  disabledStartButton () {
    return !this.state.selected
  }

  handleFilter (event) {
    this.state.startpoints.map((startpoint, i) => {
      let re = new RegExp(event.target.value, 'g')
      let res = startpoint.entity_label.toLowerCase().match(re)
      if (res == null) {
        // don't match, hide
        startpoint.hidden = true
      } else {
        // show
        startpoint.hidden = false
      }
    })
    this.forceUpdate()
  }

  render () {
    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    let redirectQueryBuilder
    if (this.state.startSession) {
      redirectQueryBuilder = <Redirect to={{
        pathname: '/query',
        state: {
          config: this.props.config,
          startpoint: this.state.selected,
          user: this.props.user,
          logged: this.props.logged
        }
      }} />
    }

    if (this.state.startSessionWithExemple) {
      redirectQueryBuilder = <Redirect to={{
        pathname: '/query',
        state: {
          redo: true,
          config: this.props.config,
          graphState: this.state.graphState,
          user: this.props.user,
          logged: this.props.logged
        }
      }} />
    }


    let errorDiv
    if (this.state.error) {
      errorDiv = (
        <div>
          <Alert color="danger">
            <i className="fas fa-exclamation-circle"></i> {this.state.errorMessage}
          </Alert>
        </div>
      )
    }

    let exempleQueries
    if (!this.state.waiting && this.state.publicQueries.length > 0) {
      exempleQueries = (
        <div>
          <p>Or start with an exemple:</p>
            <ListGroup>
              {this.state.publicQueries.map(query => (
                <ListGroupItem key={query.id} tag="button" action id={query.id} onClick={this.handleClickPublicQuery}>{query.description}</ListGroupItem>
              ))}
            </ListGroup>
        </div>
      )
    }

    let galaxyImport
    if (!this.state.waiting && this.props.user.galaxy) {
      galaxyImport = (
        <div>
          <br/>
          <p>Or import a query from Galaxy</p>
          <Button onClick={this.toggleModalGalaxy} color="secondary">Import Query</Button>
        </div>
      )
    }

    let galaxyForm
    if (this.props.user.galaxy) {
      galaxyForm = (
        <Modal size="lg" isOpen={this.state.modalGalaxy} toggle={this.toggleModalGalaxy}>
          <ModalHeader toggle={this.toggleModalGalaxy}>Upload Galaxy datasets</ModalHeader>
          <ModalBody>
            <UploadGalaxyForm config={this.props.config} getQueries={true} setStateUpload={this.props.setStateUpload} />
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModalGalaxy}>Close</Button>
          </ModalFooter>
        </Modal>
      )
    }



    let startpoints
    if (!this.state.waiting) {
      startpoints = (
        <div>
          <p>Select an entity to start a session:</p>
          <div className="startpoints-filter-div">
            <Input placeholder="Filter entities" onChange={this.handleFilter} />
          </div>
          <div className="startpoints-div">
            {this.state.startpoints.map(startpoint => (
              <div key={startpoint.entity} className="input-label" id={startpoint.entity_label}>
                <input hidden={startpoint.hidden ? 'hidden' : ''} className="startpoint-radio" value={startpoint.entity_label} type="radio" name="startpoints" id={startpoint.entity} onClick={this.handleClick}></input>
                <label hidden={startpoint.hidden ? 'hidden' : ''} className="startpoint-label" id={startpoint.name} htmlFor={startpoint.entity}>
                  {startpoint.entity_label}
                    <nodiv className="visibility-icon right">
                      {startpoint.public ? <i className="fa fa-globe-europe text-info"></i> : <nodiv></nodiv> } <nodiv> </nodiv>
                      {startpoint.private ? <i className="fa fa-lock text-primary"></i> : <nodiv></nodiv> }
                    </nodiv>
                </label>
              </div>
            ))}
          </div>
          <br />
          <Button disabled={this.disabledStartButton()} onClick={this.handleStart} color="secondary">Start!</Button>
        </div>
      )
    }

    return (
      <div className="container">
        {redirectQueryBuilder}
        {redirectLogin}
        <h2>Ask!</h2>
        <hr />
        <WaitingDiv waiting={this.state.waiting} center />
          <Row>
            <Col xs="4">
              {startpoints}
              {galaxyImport}
              {galaxyForm}
            </Col>
            <Col xs="8">
              {exempleQueries}
            </Col>
          </Row>
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

Ask.propTypes = {
  waitForStart: PropTypes.bool,
  user: PropTypes.object,
  config: PropTypes.object,
  logged: PropTypes.bool
}
