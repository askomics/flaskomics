import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button, ButtonGroup, Spinner } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import PropTypes from 'prop-types'
import update from 'immutability-helper'

import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'

import AceEditor from 'react-ace'
import ReactResizeDetector from 'react-resize-detector';

import "ace-builds/src-noconflict/mode-sparql";
import "ace-builds/src-noconflict/theme-tomorrow";

import dedent from 'dedent'

import ResultsTable from './resultstable'
import AdvancedSparql from './advancedsparql'
import Utils from '../../classes/utils'

export default class Sparql extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      config: this.props.config,
      results_data: [],
      results_header: [],
      error: false,
      errorMessage: null,
      sparqlInput: "",
      graphs: {},
      endpoints: {},
      exceededQuota: false,
      diskSpace: 0,
      console_enabled: false,

      // save query icons
      disableSave: false,
      saveIcon: "play",

      // Preview icons
      disablePreview: false,
      previewIcon: "table",

      editorHeight: 500,
      editorWidth: "auto",

      waiting: true
    }
    this.cancelRequest
    this.handleCodeChange = this.handleCodeChange.bind(this)
    this.previewQuery = this.previewQuery.bind(this)
    this.launchQuery = this.launchQuery.bind(this)
    this.onResize = this.onResize.bind(this)
    this.handleChangeGraphs = this.handleChangeGraphs.bind(this)
    this.handleChangeEndpoints = this.handleChangeEndpoints.bind(this)
  }

  componentDidMount () {
    if (this.props.location.state) {
      this.setState({
        sparqlInput: this.props.location.state.sparqlQuery,
        graphs: this.props.location.state.graphs,
        endpoints: this.props.location.state.endpoints,
        diskSpace: this.props.location.state.diskSpace,
        config: this.props.location.state.config,
        console_enabled: this.console_enabled,
        waiting: false,
      })
    } else {
      let requestUrl = '/api/sparql/init'
      axios.get(requestUrl, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
          console.log(requestUrl, response.data)
          this.setState({
            sparqlInput: response.data.defaultQuery,
            graphs: response.data.graphs,
            endpoints: response.data.endpoints,
            diskSpace: response.data.diskSpace,
            waiting: false,
            error: response.data.error,
            errorMessage: response.data.errorMessage,
            config: this.props.config,
            status: response.status,
            console_enabled: response.console_enabled
          })
        })
        .catch(error => {
          console.log(error, error.response.data.errorMessage)
          this.setState({
            error: true,
            errorMessage: error.response.data.errorMessage,
            status: error.response.status
          })
        })
    }
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      if (this.utils.isFunction(this.cancelRequest)) {
        this.cancelRequest()
      }
    }
  }

  handleCodeChange (code) {
    this.setState({
      disableSave: false,
      saveIcon: "play",
      disablePreview: false,
      previewIcon: "table",
      sparqlInput: code,
      error: false,
      errorMessage: null
    }, () => {
      if (this.utils.isFunction(this.cancelRequest)) {
        this.cancelRequest()
      }
    })
  }

  get_selected_graphs () {
    let graphs = []
    Object.keys(this.state.graphs).map((key, index) => {
      if (this.state.graphs[key]["selected"]) {
        graphs.push(key)
      }
    })
    return graphs
  }

  get_selected_endpoints () {
    let endpoints = []
    Object.keys(this.state.endpoints).map((key, index) => {
      if (this.state.endpoints[key]["selected"]) {
        endpoints.push(key)
      }
    })
    return endpoints
  }

  previewQuery () {
    let requestUrl = '/api/sparql/previewquery'
    let data = {
      query: this.state.sparqlInput,
      graphs: this.get_selected_graphs(),
      endpoints: this.get_selected_endpoints()
    }
    this.setState({
      disablePreview: true,
      previewIcon: "spinner"
    })
    axios.post(requestUrl, data, { baseURL: this.state.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          results_data: response.data.data,
          results_header: response.data.header,
          waiting: false,
          error: false,
          previewIcon: "check text-success"
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          results_data: [],
          results_header: [],
          waiting: false,
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          previewIcon: "times text-error",
          disablePreview: false
        })
      })
  }

  launchQuery () {
    let requestUrl = '/api/sparql/savequery'
    let data = {
      query: this.state.sparqlInput,
      graphs: this.get_selected_graphs(),
      endpoints: this.get_selected_endpoints()
    }
    this.setState({
      disableSave: true,
      saveIcon: "spinner"
    })
    axios.post(requestUrl, data, { baseURL: this.state.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          results_data: [],
          results_header: [],
          waiting: false,
          error: false,
          saveIcon: "check text-success"
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          results_data: [],
          results_header: [],
          waiting: false,
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          saveIcon: "times text-error",
          disableSave: false,
        })
      })
  }

  handleChangeGraphs (event) {
    this.setState({
      graphs: update(this.state.graphs, {[event.target.value]: {selected: {$set: event.target.checked}}}),
      disableSave: false,
      saveIcon: "play",
      disablePreview: false,
      previewIcon: "table",
    })
  }


  handleChangeEndpoints (event) {
    this.setState({
      endpoints: update(this.state.endpoints, {[event.target.value]: {selected: {$set: event.target.checked}}}),
      disableSave: false,
      saveIcon: "play",
      disablePreview: false,
      previewIcon: "table",
    })
  }

  onResize (w, h) {
    this.setState({
      editorHeight: h,
      editorWidth: w
    })
  }

  render () {
    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    let resultsTable
    if (this.state.results_header.length > 0) {
      resultsTable = (
        <ResultsTable data={this.state.results_data} header={this.state.results_header} />
      )
    }

    // Warning disk space
    let warningDiskSpace
    if (this.state.exceededQuota) {
      warningDiskSpace = (
        <div>
          <Alert color="warning">
              Your files (uploaded files and results) take {this.utils.humanFileSize(this.state.diskSpace, true)} of space
              (you have {this.utils.humanFileSize(this.state.config.user.quota, true)} allowed).
              Please delete some before save queries or contact an admin to increase your quota
          </Alert>
        </div>
      )
    }

    // icons
    let previewIcon = <i className={"fas fa-" + this.state.previewIcon}></i>
    if (this.state.previewIcon == "spinner") {
      previewIcon = <Spinner size="sm" color="light" />
    }

    // launch buttons
    let previewButton
    let launchQueryButton
    if (this.state.console_enabled){
      previewButton = <Button onClick={this.previewQuery} color="secondary" disabled={this.state.disablePreview}>{previewIcon} Run & preview</Button>
      launchQueryButton = <Button onClick={this.launchQuery} color="secondary" disabled={this.state.disableSave || this.state.exceededQuota}><i className={"fas fa-" + this.state.saveIcon}></i> Run & save</Button>
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>SPARQL query</h2>
        <hr />
        <br />
        {warningDiskSpace}
        <div className="resizable">
          <ReactResizeDetector handleWidth handleHeight onResize={this.onResize} />
          <AceEditor
            mode="sparql"
            theme="tomorrow"
            onChange={this.handleCodeChange}
            name="sparqlQuery"
            fontSize={18}
            showPrintMargin={true}
            showGutter={true}
            highlightActiveLine={true}
            value={this.state.sparqlInput}
            editorProps={{ $blockScrolling: true }}
            height={this.state.editorHeight}
            width={this.state.editorWidth}
            readOnly={!this.state.console_enabled}
          />
        </div>
        <br />
        <AdvancedSparql
          config={this.state.config}
          graphs={this.state.graphs}
          endpoints={this.state.endpoints}
          handleChangeGraphs={this.handleChangeGraphs}
          handleChangeEndpoints={this.handleChangeEndpoints}
        />
        <br />
        <ButtonGroup>
            {previewButton}
            {launchQueryButton}
        </ButtonGroup>
        <br />
        <br />

        {resultsTable}

        <WaitingDiv waiting={this.state.waiting} center />
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} customMessages={{"504": "Query time is too long, use Run & Save to get your results", "502": "Query time is too long, use Run & Save to get your results"}} />
      </div>
    )
  }
}

Sparql.propTypes = {
  location: PropTypes.object,
  config: PropTypes.object,
  waitForStart: PropTypes.bool,
}
