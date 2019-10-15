import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button, ButtonGroup } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import PropTypes from 'prop-types'

import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'

import brace from 'brace'
import AceEditor from 'react-ace'

import 'brace/mode/sparql'
import 'brace/theme/tomorrow'

import dedent from 'dedent'

import ResultsTable from './resultstable'
import Utils from '../../classes/utils'

export default class Sparql extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      config: this.props.location.state.config,
      results_data: [],
      results_header: [],
      error: false,
      errorMessage: null,
      sparqlInput: this.props.location.state.sparqlQuery,
      exceededQuota: this.props.location.state.config.user.quota > 0 && this.props.location.state.diskSpace >= this.props.location.state.config.user.quota,
      diskSpace: this.props.location.state.diskSpace,
      // save query icons
      disableSave: false,
      saveIcon: "play",

      // Preview icons
      disablePreview: false,
      previewIcon: "table"
    }
    this.handleCodeChange = this.handleCodeChange.bind(this)
    this.previewQuery = this.previewQuery.bind(this)
    this.launchQuery = this.launchQuery.bind(this)
  }

  handleCodeChange (code) {
    this.setState({
      disableSave: false,
      saveIcon: "play",
      disablePreview: false,
      previewIcon: "table",
      sparqlInput: code
    })
  }

  previewQuery () {
    let requestUrl = '/api/sparql/previewquery'
    let data = {
      query: this.state.sparqlInput
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
          previewIcon: "times text-error"
        })
      })
  }

  launchQuery () {
    let requestUrl = '/api/sparql/savequery'
    let data = {
      query: this.state.sparqlInput
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
          saveIcon: "times text-error"
        })
      })
  }

  render () {
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

    return (
      <div className="container">
        <h2>SPARQL query</h2>
        <hr />
        <br />
        {warningDiskSpace}
        <div>
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
            height={400}
            width={'auto'}
          />
        </div>

        <br />
        <ButtonGroup>
          <Button onClick={this.previewQuery} color="secondary" disabled={this.state.disablePreview}><i className={"fas fa-" + this.state.previewIcon}></i> Run & preview</Button>
          <Button onClick={this.launchQuery} color="secondary" disabled={this.state.disableSave || this.state.exceededQuota}><i className={"fas fa-" + this.state.saveIcon}></i> Run & save</Button>
        </ButtonGroup>
        <br />
        <br />

        {resultsTable}

        <WaitingDiv waiting={this.state.waiting} center />
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

Sparql.propTypes = {
  location: PropTypes.object,
}