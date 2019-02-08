import React, { Component } from 'react';
import { Form, FormGroup, FormText, Label, Input, Button } from 'reactstrap'
import axios from 'axios'


export default class UploadForm extends Component {
  constructor(props) {
    super(props)

    this.state = {
      files: [],
      new_files: []
    }

    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }


  handleChange(event) {
    this.setState({
      new_files: event.target.files
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
            <Input type="file" name="file" id="files" onChange={this.handleChange} multiple/>
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
