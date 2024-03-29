import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Input, Button, ButtonGroup } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import UploadModal from './uploadmodal'
import FilesTable from './filestable'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'

export default class Upload extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      error: false,
      errorMessage: null,
      integration: false,
      files: [],
      exceededQuota: false,
      selected: [],
      waiting: true
    }
    this.deleteSelectedFiles = this.deleteSelectedFiles.bind(this)
    this.integrateSelectedFiles = this.integrateSelectedFiles.bind(this)
    this.getFiles = this.getFiles.bind(this)
    this.cancelRequest
  }

  componentDidMount () {
    if (!this.props.waitForStart) {
      this.interval = setInterval(() => {
        this.getFiles()
      }, 5000)
      this.getFiles()
    }
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }


  getFiles() {
    let requestUrl = '/api/files'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          diskSpace: response.data.diskSpace,
          exceededQuota: this.props.config.user.quota > 0 && response.data.diskSpace >= this.props.config.user.quota,
          files: response.data.files,
          waiting: false
        })
        let isProcessing = response.data.files.some(file => file.status == "processing")
        console.log(isProcessing)
        if (this.interval && !isProcessing){
          clearInterval(this.interval)
          this.interval = ""
        }
        if (!this.interval && isProcessing){
          this.interval = setInterval(() => {
            this.getFiles()
          }, 5000)
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


  deleteSelectedFiles () {
    let requestUrl = '/api/files/delete'
    let data = {
      filesIdToDelete: this.state.selected
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          files: response.data.files,
          selected: [],
          error: response.data.error,
          errorMessage: response.data.errorMessage
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          selected: []
        })
      })
  }

  integrateSelectedFiles () {
    console.log(this.state.selected)
    this.setState({
      integration: true
    })
  }

  isDisabled () {
    return this.state.selected.length == 0
  }

  isDisabledIntegrate () {
    return this.state.selected.length == 0 || this.state.files.some(file => this.state.selected.includes(file.id) && file.status == "error")
  }

  render () {
    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    let redirectIntegration
    if (this.state.integration) {
      redirectIntegration = <Redirect to={{
        pathname: '/integration',
        state: {
          filesId: this.state.selected,
          config: this.props.config
        }
      }} />
    }


    let warningDiskSpace
    if (this.state.exceededQuota) {
      warningDiskSpace = (
        <div>
          <Alert color="warning">
              Your files (uploaded files and results) take {this.utils.humanFileSize(this.state.diskSpace, true)} of space 
              (you have {this.utils.humanFileSize(this.props.config.user.quota, true)} allowed). 
              Please delete some before uploading or contact an admin to increase your quota
          </Alert>
        </div>
      )
    }

    return (
      <div className="container">
        {redirectLogin}
        {redirectIntegration}
        <h2>Upload</h2>
        <hr />
        {warningDiskSpace}
        <UploadModal disabled={this.state.exceededQuota} setStateUpload={p => this.setState(p)} config={this.props.config} getFiles={this.getFiles} />
        <hr />
        <FilesTable files={this.state.files} setStateUpload={p => this.setState(p)} selected={this.state.selected} waiting={this.state.waiting} config={this.props.config} />
        <br />
        <ButtonGroup>
          <Button disabled={this.isDisabled()} onClick={this.deleteSelectedFiles} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
          <Button disabled={this.isDisabledIntegrate()} onClick={this.integrateSelectedFiles} color="secondary"><i className="fas fa-database"></i> Integrate</Button>
        </ButtonGroup>
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

Upload.propTypes = {
  config: PropTypes.object,
  waitForStart: PropTypes.bool
}
