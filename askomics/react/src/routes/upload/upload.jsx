import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Input, Button, ButtonGroup } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import UploadModal from './uploadmodal'
import FilesTable from './filestable'
import PropTypes from 'prop-types'
import AskoContext from '../../components/context'

export default class Upload extends Component {
  static contextType = AskoContext
  constructor (props) {
    super(props)
    this.state = {
      error: false,
      errorMessage: null,
      logged: props.logged,
      user: props.user,
      integration: false,
      files: [],
      selected: [],
      waiting: true
    }
    this.deleteSelectedFiles = this.deleteSelectedFiles.bind(this)
    this.integrateSelectedFiles = this.integrateSelectedFiles.bind(this)
    this.cancelRequest
  }

  componentDidMount () {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/files'
      axios.get(requestUrl, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
          console.log(requestUrl, response.data)
          this.setState({
            files: response.data.files,
            waiting: false
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
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  deleteSelectedFiles () {
    let requestUrl = '/api/files/delete'
    let data = {
      filesIdToDelete: this.state.selected
    }
    axios.post(requestUrl, data, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
          user: this.props.user,
          logged: this.props.logged
        }
      }} />
    }

    return (
      <div className="container">
        {redirectLogin}
        {redirectIntegration}
        <h2>Upload</h2>
        <hr />
        <UploadModal setStateUpload={p => this.setState(p)} />
        <hr />
        <FilesTable files={this.state.files} setStateUpload={p => this.setState(p)} selected={this.state.selected} waiting={this.state.waiting} />
        <br />
        <ButtonGroup>
          <Button disabled={this.isDisabled()} onClick={this.deleteSelectedFiles} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
          <Button disabled={this.isDisabled()} onClick={this.integrateSelectedFiles} color="secondary"><i className="fas fa-database"></i> Integrate</Button>
        </ButtonGroup>
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

Upload.propTypes = {
  logged: PropTypes.bool,
  user: PropTypes.object,
  waitForStart: PropTypes.bool
}
