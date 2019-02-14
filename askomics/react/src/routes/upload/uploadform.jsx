import React, { Component } from 'react';
import { Form, FormGroup, FormText, Label, Input, Button, CustomInput } from 'reactstrap'
import axios from 'axios'


export default class UploadForm extends Component {
  constructor(props) {
    super(props)

    this.state = {
      files: [],
      new_files: [],
      label: "Browse files"
    }

    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }


  handleChange(event) {

    let nselected = event.target.files.length
    let label = nselected + " file selected"
    if (nselected > 1) {
      label = nselected + " files selected"
    }

    this.setState({
      new_files: event.target.files,
      label: label
    })
  }

  handleSubmit(event) {

    event.preventDefault()

    let requestUrl = '/api/files/upload'
    let data = new FormData()

    for (let i = this.state.new_files.length - 1; i >= 0; i--) {
      console.log(this.state.new_files[i].name)
      data.append(this.state.new_files[i].name, this.state.new_files[i])
    }

    axios.post(requestUrl, data)
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        error: response.data.error,
        files: response.data.uploadedFiles,
        errorMessage: response.data.errorMessage,
      })
      this.props.setStateUpload({
        files: this.state.files
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status,
        success: !response.data.error
      })
    })
    event.preventDefault()
  }


  render() {
    return (
      <div>
        <Form onSubmit={this.handleSubmit}>
          <FormGroup>
            <CustomInput type="file" id="files" name="file" label={this.state.label} onChange={this.handleChange} multiple/>
            <FormText color="muted">
              <p>Supported files: CSV/TSV, GFF and TTL</p>
              <p>The maximum file size is 4GB</p>
            </FormText>
          </FormGroup>
          <Button color="secondary">Upload</Button>
        </Form>
      </div>
    )

  }
}
