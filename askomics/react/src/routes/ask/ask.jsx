import React, { Component, lazy, Suspense } from 'react'
import axios from 'axios'
import DOMPurify from 'dompurify'
import { Alert, Badge, Button, InputGroupAddon, Input, InputGroup, Row, Col, ListGroup, ListGroupItem, Modal, ModalHeader, ModalBody, ModalFooter, ButtonDropdown, DropdownToggle, DropdownMenu, DropdownItem, InputGroupButtonDropdown } from 'reactstrap'
import { Redirect, Link } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import Template from '../../components/template'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import UploadGalaxyForm from '../upload/uploadgalaxyform'
import Utils from '../../classes/utils'

export default class Ask extends Component {
  constructor (props) {
    super(props)
    this.state = {
      waiting: true,
      error: false,
      errorMessage: null,
      startpoints: [],
      endpoints: [],
      selected: null,
      startSession: false,
      publicQueries: [],
      publicFormQueries: [],
      modalGalaxy: false,
      showGalaxyButton: false,
      dropdownOpen: false,
      selectedEndpoint: [],
      redirectFormBuilder: false,
      console_enabled: false
    }
    this.utils = new Utils()
    this.cancelRequest
    this.handleClick = this.handleClick.bind(this)
    this.handleStart = this.handleStart.bind(this)
    this.handleFilter = this.handleFilter.bind(this)
    this.handleClickTemplateQuery = this.handleClickTemplateQuery.bind(this)
    this.handleClickTemplateFormQuery = this.handleClickTemplateFormQuery.bind(this)
    this.toggleDropDown = this.toggleDropDown.bind(this)
    this.toggleModalGalaxy = this.toggleModalGalaxy.bind(this)
    this.clickOnEndpoint = this.clickOnEndpoint.bind(this)
  }

  componentDidMount () {

    if (this.props.config.user) {
      if (this.props.config.user.galaxy) {
        this.setState({
          showGalaxyButton: true
        })
      }
    }

    if (!this.props.waitForStart) {
      let requestUrl = '/api/query/startpoints'
      axios.get(requestUrl, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
          console.log(requestUrl, response.data)

          let endpoints = []
          response.data.startpoints.forEach(startpoint => {
            startpoint.endpoints.forEach(endpoint => {
              endpoints.push(endpoint.name)
            })
          })
          endpoints = [...new Set(endpoints)]
          this.setState({
            selectedEndpoint: endpoints
          })

          this.setState({
            waiting: false,
            endpoints: endpoints,
            startpoints: response.data.startpoints.map(startpoint => new Object({
              graphs: startpoint.graphs,
              endpoints: Array.from(new Set(startpoint.endpoints.map(JSON.stringify))).map(JSON.parse),
              entity: startpoint.entity,
              entity_label: startpoint.entity_label,
              public: startpoint.public,
              private: startpoint.private,
              hidden: false,
              selected: false
            })),
            publicQueries: response.data.publicQueries,
            publicFormQueries: response.data.publicFormQueries,
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

  handleClickTemplateQuery (event) {
    // request api to get a preview of file
    let requestUrl = '/api/results/getquery'
    let data = { fileId: event.target.id }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        // set state of resultsPreview
        if (response.data.sparqlQuery == null) {
          this.setState({
            startSessionWithExemple: true,
            graphState: response.data.graphState
          })
        } else {
          this.setState({
            startSPARQLWithExemple: true,
            sparqlQuery: response.data.sparqlQuery,
            graphs: response.data.graphs,
            endpoints_sparql: response.data.endpoints,
            diskSpace: response.data.diskSpace,
            console_enabled: response.data.console_enabled
          })
        }
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

  handleClickTemplateFormQuery (event) {
    let requestUrl = '/api/results/graphstate'
    let data = { fileId: event.target.id, formated: false }
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        // set state of resultsPreview
        this.setState({
          redirectFormBuilder: true,
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

  toggleDropDown() {
    this.setState({
      dropdownOpen: ! this.state.dropdownOpen
    })
  }

  clickOnEndpoint(event) {
    let value = event.target.value
    let array = this.state.selectedEndpoint
    if (array.includes(value)) {
      let index = array.indexOf(value)
      array.splice(index, 1)
    }else {
      array.push(value)
    }

    this.setState({
      selectedEndpoint: array
    })

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
          startpoint: this.state.selected
        }
      }} />
    }

    if (this.state.startSessionWithExemple) {
      redirectQueryBuilder = <Redirect to={{
        pathname: '/query',
        state: {
          redo: true,
          config: this.props.config,
          graphState: this.state.graphState
        }
      }} />
    }

    let redirectSparqlEditor
    if (this.state.startSPARQLWithExemple) {
      redirectSparqlEditor = <Redirect to={{
        pathname: '/sparql',
        state: {
          sparqlQuery: this.state.sparqlQuery,
          graphs: this.state.graphs,
          endpoints: this.state.endpoints_sparql,
          diskSpace: this.state.diskSpace,
          config: this.props.config,
          console_enabled: this.state.console_enabled
        }
      }} />
    }

    let redirectFormBuilder
    if (this.state.redirectFormBuilder) {
      redirectFormBuilder = <Redirect to={{
        pathname: '/form',
        state: {
          config: this.props.config,
          graphState: this.state.graphState
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

    let templateQueries
    let templateFormQueries
    let emptyPrivate
    if (!this.state.waiting && this.state.publicQueries.length > 0) {
      templateQueries = (
        <div>
          <p>Or start with a template:</p>
            <ListGroup>
              {this.state.publicQueries.map(query => {
                if (query.public == 0) {
                  emptyPrivate = <br />
                  return <ListGroupItem key={query.id} tag="button" action id={query.id} onClick={this.handleClickTemplateQuery}>{query.description}</ListGroupItem>
                }
              })}
            </ListGroup>
            {emptyPrivate}
            <ListGroup>
              {this.state.publicQueries.map(query => {
                if (query.public == 1) {
                  return <ListGroupItem key={query.id} tag="button" action id={query.id} onClick={this.handleClickTemplateQuery}>{query.description}</ListGroupItem>
                }
              })}
            </ListGroup>
        </div>
      )
    }

    if (!this.state.waiting && this.state.publicFormQueries.length > 0) {
      templateFormQueries = (
        <div>
          <p>Or start with a simplified form:</p>
            <ListGroup>
              {this.state.publicFormQueries.map(query => {
                if (query.public == 0) {
                  emptyPrivate = <br />
                  return <ListGroupItem key={query.id} tag="button" action id={query.id} onClick={this.handleClickTemplateFormQuery}>{query.description}</ListGroupItem>
                }
              })}
            </ListGroup>
            {emptyPrivate}
            <ListGroup>
              {this.state.publicFormQueries.map(query => {
                if (query.public == 1) {
                  return <ListGroupItem key={query.id} tag="button" action id={query.id} onClick={this.handleClickTemplateFormQuery}>{query.description}</ListGroupItem>
                }
              })}
            </ListGroup>
        </div>
      )
    }

    let galaxyImport
    if (!this.state.waiting && this.state.showGalaxyButton) {
      galaxyImport = (
        <div>
          <br/>
          <p>Or import a query from <a href={this.props.config.user.galaxy.url}>Galaxy</a></p>
          <Button onClick={this.toggleModalGalaxy} color="secondary">Import Query</Button>
        </div>
      )
    }

    let galaxyForm
    if (this.state.showGalaxyButton) {
      galaxyForm = (
        <Modal size="lg" isOpen={this.state.modalGalaxy} toggle={this.toggleModalGalaxy}>
          <ModalHeader toggle={this.toggleModalGalaxy}>Upload Galaxy datasets</ModalHeader>
          <ModalBody>
            <UploadGalaxyForm config={this.props.config} getQueries={true} />
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModalGalaxy}>Close</Button>
          </ModalFooter>
        </Modal>
      )
    }

    let startpoints
    if (!this.state.waiting) {
      if (this.props.config.protectPublic && !this.props.config.logged) {
        startpoints = (
          <div>
          <Alert color="info">
            This instance is available only for logged user. <Link to="/login">Login</Link>
            {this.props.config.disableAccountCreation ? <nodiv></nodiv> : <> or <Link to="/signup">signup</Link></>}
            <nodiv> to use.</nodiv>
          </Alert>
          </div>
        )
      } else {
        startpoints = (
          <div>
            <p>Select an entity to start a session:</p>
            <div className="startpoints-filter-div">

            <InputGroup>
              <InputGroupButtonDropdown isOpen={this.state.dropdownOpen} toggle={this.toggleDropDown}>
                <DropdownToggle outline caret>
                  Source
                </DropdownToggle>
                <DropdownMenu>
                {this.state.endpoints.map(endpoint => {

                  let tick = <i className={this.state.selectedEndpoint.includes(endpoint) ? "fas fa-check" : "icon-invisible fas fa-check"}></i>

                  return (
                    <DropdownItem key={endpoint} value={endpoint} onClick={this.clickOnEndpoint}>
                      {tick} {endpoint}
                    </DropdownItem>
                  )
                })}
                </DropdownMenu>
              </InputGroupButtonDropdown>
              <Input placeholder="Filter entities" onChange={this.handleFilter} />
            </InputGroup>

            </div>
            <div className="startpoints-div">
              {this.state.startpoints.map(startpoint => {
                let display = false
                startpoint.endpoints.forEach(endpoint => {
                  if (this.state.selectedEndpoint.includes(endpoint.name)) {
                    display = true
                  }
                })
                return (
                <div key={startpoint.entity} className="input-label" id={startpoint.entity_label}>
                <input className="startpoint-radio" value={startpoint.entity_label} type="radio" name="startpoints" id={startpoint.entity} onClick={this.handleClick}></input>
                <label className="startpoint-label" id={startpoint.name} htmlFor={startpoint.entity}>
                <table hidden={startpoint.hidden ? 'hidden' : display ? '' : 'hidden'} className="startpoint-table">
                  <tr>
                    <td className="startpoint-table cell1">
                        {startpoint.entity_label}
                    </td>
                    <td className="startpoint-table cell2">
                      {startpoint.endpoints.map(endpoint => {
                        let color = this.utils.stringToHexColor(endpoint.url)
                        let textColor = this.utils.isDarkColor(color) ? "white" : "black"
                        return <h6 key={endpoint.url}><Badge style={{"background-color": color, "color": textColor}}>{endpoint.name}</Badge></h6>
                      })}
                    </td>
                    <td className="startpoint-table cell3">
                      <nodiv className="visibility-icon right">
                        {startpoint.public ? <i className="fa fa-globe-europe text-info"></i> : <nodiv></nodiv> } <nodiv> </nodiv>
                        {startpoint.private ? <i className="fa fa-lock text-primary"></i> : <nodiv></nodiv> }
                      </nodiv>
                    </td>
                  </tr>
                </table>
                </label>
                </div>
              )})}
            </div>
            <br />
            <Button disabled={this.disabledStartButton()} onClick={this.handleStart} color="secondary">Start!</Button>
          </div>
        )
      }
    }

    let HtmlFrontMessage = (
      <div>
        <h2>Ask!</h2>
        <Template template={this.props.config.frontMessage}/>
        <hr />
      </div>
    )

    return (
      <div className="container">
        {redirectQueryBuilder}
        {redirectLogin}
        {redirectSparqlEditor}
        {redirectFormBuilder}
        {HtmlFrontMessage}
        <WaitingDiv waiting={this.state.waiting} center />
          <Row>
            <Col xs="5">
              {startpoints}
              {galaxyImport}
              {galaxyForm}
            </Col>
            <Col xs="7">
              {templateFormQueries}
              {templateQueries}
            </Col>
          </Row>
          <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

Ask.propTypes = {
  waitForStart: PropTypes.bool,
  config: PropTypes.object,
}
