import React, { Component } from 'react'
import { Form, FormGroup, FormText, Label, Input, Button, CustomInput, Progress } from 'reactstrap'
import axios from 'axios'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import ErrorDiv from '../error/error'

export default class UploadForm extends Component {
  constructor (props) {
    super(props)

    this.state = {
      files: [],
      new_files: [],
      label: 'Browse files',
      error: false,
      errorMessage: null,
      status: null
    }

    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }

  handleChange (event) {
    let nselected = event.target.files.length
    let label = nselected + ' file selected'
    if (nselected > 1) {
      label = nselected + ' files selected'
    }

    this.setState({
      // new_files: event.target.files,
      new_files: Array.from(event.target.files).map(file => new Object({
        file: file,
        name: file.name,
        size: file.size,
        uploadPercentage: 0,
        path: '',
        error: false,
        errorMessage: ''
      })),
      label: label
    })
  }

  handleSubmit (event) {
    event.preventDefault()

    let requestUrlUpload = '/api/files/upload_chunk'
    // let data = new FormData()

    for (let i = this.state.new_files.length - 1; i >= 0; i--) {
      let loaded = 0
      let chunkSize = 1024 * 1024 * 10 // 10 MB
      let file = this.state.new_files[i].file
      let totalSize = this.state.new_files[i].size
      let start = 0
      let reader = new FileReader()
      let blob = file.slice(start, chunkSize)
      let first = true
      let last = false

      if (totalSize <= chunkSize) {
        last = true
      }

      reader.readAsText(blob)
      reader.onload = (event) => {
        let data = {
          chunk: reader.result,
          name: this.state.new_files[i].name,
          path: this.state.new_files[i].path,
          first: first,
          last: last,
          type: this.state.new_files[i].file.type,
          size: totalSize
        }
        axios.post(requestUrlUpload, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
          .then(response => {
            console.log(requestUrlUpload, response.data)
            first = false
            loaded += chunkSize
            // update precentage
            this.setState({
              new_files: update(this.state.new_files, { [i]: { uploadPercentage: { $set: Math.round((loaded / totalSize) * 100) } } })
            })
            // FIXME: use one setState
            this.setState({
              new_files: update(this.state.new_files, { [i]: { path: { $set: response.data.path } } })
            })
            if (loaded <= totalSize) {
              blob = file.slice(loaded, loaded + chunkSize)
              if (totalSize - loaded <= chunkSize) {
                last = true
              }
              reader.readAsText(blob)
            } else {
              loaded = totalSize
              this.setState({
                new_files: update(this.state.new_files, { [i]: { uploadPercentage: { $set: 100 } } })
              })
              // load file component
              this.props.getFiles()
            }
          }).catch(error => {
            console.log(error, error.response.data.errorMessage)
            this.setState({
              error: true,
              errorMessage: error.response.data.errorMessage,
              status: error.response.status
            })
          })
      }
    }
    event.preventDefault()
  }

  render () {
    return (
      <div>
        <Form onSubmit={this.handleSubmit}>
          <FormGroup>
            <CustomInput type="file" id="files" name="file" label={this.state.label} onChange={this.handleChange} multiple/>
            <FormText color="muted">
              <p>Supported files: CSV/TSV, GFF3, BED and TTL</p>
              <p>The maximum file size is 4GB</p>
            </FormText>
            {this.state.new_files.map(file => {
              let progressBar
              if (file.error) {
                progressBar = <Progress color="error" value="100">ERROR</Progress>
              } else {
                progressBar = <Progress color="success" value={file.uploadPercentage}>{file.uploadPercentage} %</Progress>
              }
              return (
                <div key={file.id}>
                  <div className="text-center">{file.name}</div>
                  {progressBar}
                </div>
              )
            })}
          </FormGroup>
          <Button color="secondary">Upload</Button>
        </Form>
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

UploadForm.propTypes = {
  setStateUpload: PropTypes.func,
  getFiles: PropTypes.func,
  config: PropTypes.object
}
