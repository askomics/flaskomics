import React, { Component } from 'react';
import { Form, FormGroup, FormText, Label, Input, Button, CustomInput, Progress } from 'reactstrap'
import axios from 'axios'
import update from 'react-addons-update'

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

    console.log('files', event.target.files)

    this.setState({
      // new_files: event.target.files,
      new_files: Array.from(event.target.files).map(file => new Object({
        file: file,
        name: file.name,
        size: file.size,
        uploadPercentage: 0,
        path: ''
      })),
      label: label
    })

    console.log('state', this.state)
  }


  handleSubmit(event) {

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

      reader.readAsBinaryString(blob)
      console.log(this.state.new_files[i])
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
        axios.post(requestUrlUpload, data)
        .then(response => {
          console.log(requestUrlUpload, response.data)
          first = false
          loaded += chunkSize
          // update precentage
          this.setState({
            new_files: update(this.state.new_files, {[i]: {uploadPercentage: {$set: Math.round((loaded / totalSize) * 100)}}}),
          })
          //FIXME: use one setState
          this.setState({
            new_files: update(this.state.new_files, {[i]: {path: {$set: response.data.path}}})
          })
          if (loaded <= totalSize) {
            blob = file.slice(loaded, loaded + chunkSize)
            if (totalSize - loaded <= chunkSize) {
              last = true
            }
            reader.readAsBinaryString(blob)
          } else {
            loaded = totalSize
            this.setState({
              new_files: update(this.state.new_files, {[i]: {uploadPercentage: {$set: 100}}})
            })
            // load file component
            let requestUrlFiles = '/api/files'
            axios.get(requestUrlFiles, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
            .then(response => {
              console.log(requestUrlFiles, response.data)
              this.props.setStateUpload({
                files: response.data.files
              })
            })
            .catch(error => {
              console.log(error, error.response.data.errorMessage)
            })





          }
        })
      }


// this.setState({
//   items: update(this.state.items, {1: {name: {$set: 'updated field name'}}})
// })



      // console.log(this.state.new_files[i].name)
      // data.append(this.state.new_files[i].name, this.state.new_files[i])
    }

    // axios.post(requestUrl, data)
    // .then(response => {
    //   console.log(requestUrl, response.data)
    //   this.setState({
    //     error: response.data.error,
    //     files: response.data.uploadedFiles,
    //     errorMessage: response.data.errorMessage,
    //   })
    //   this.props.setStateUpload({
    //     files: this.state.files
    //   })
    // })
    // .catch(error => {
    //   console.log(error, error.response.data.errorMessage)
    //   this.setState({
    //     error: true,
    //     errorMessage: error.response.data.errorMessage,
    //     status: error.response.status,
    //     success: !response.data.error
    //   })
    // })
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
            {this.state.new_files.map(file => {
              return (
                <div>
                  <div className="text-center">{file.name}</div>
                  <Progress color="success" value={file.uploadPercentage}>{file.uploadPercentage} %</Progress>
                </div>
              )
            })}
          </FormGroup>
          <Button color="secondary">Upload</Button>
        </Form>
      </div>
    )

  }
}
