import React, { Component } from 'react'
import { Form, FormGroup, FormText, Label, Input, Button, CustomInput, Progress } from 'reactstrap'
import axios from 'axios'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'
import ErrorDiv from '../error/error'

export default class UploadUrlForm extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()

    this.state = {
      url: '',
      disabled: true,
      progressAnimated: true,
      progressValue: 0,
      progressDisplay: "",
      progressColor: "success",
      error: false,
      errorMessage: null,
      status: null
    }

    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
    this.cancelRequest
  }

  handleChange (event) {
    this.setState({
      url: event.target.value,
      disabled: !this.utils.isUrl(event.target.value)
    })
  }

  handleSubmit (event) {

    let requestUrl = '/api/files/upload_url'
    let data = {
      url: this.state.url
    }

    this.setState({
      disabled: true,
      progressAnimated: true,
      progressValue: 99,
      progressDisplay: "99 %",
      progressColor: "success"
    })

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          disabled: false,
          progressAnimated: false,
          progressValue: 100,
          progressDisplay: "100 %",
          progressColor: "success"
        })

        // load file component
        let requestUrlFiles = '/api/files'
        axios.get(requestUrlFiles, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
          .then(response => {
            console.log(requestUrlFiles, response.data)
            this.props.setStateUpload({
              files: response.data.files
            })
          })
          .catch(error => {
            console.log(error, error.response.data.errorMessage)
          })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          disabled: false,
          progressAnimated: false,
          progressValue: 100,
          progressDisplay: "ERROR",
          progressColor: "error",
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
        })
      })

  }

  render () {
    return (
      <div>
        <Input onChange={this.handleChange} value={this.state.url} type="url" name="url" id="url" placeholder="Enter file URL" />
        <Progress animated={this.state.progressAnimated} color={this.state.progressColor} value={this.state.progressValue}>{this.state.progressDisplay}</Progress>
        <br />
        <Button disabled={this.state.disabled} onClick={this.handleSubmit} color="secondary">Upload</Button>
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

UploadUrlForm.propTypes = {
  setStateUpload: PropTypes.func,
  config: PropTypes.object
}
