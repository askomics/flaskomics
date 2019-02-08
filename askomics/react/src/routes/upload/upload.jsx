import React, { Component } from "react"
import axios from 'axios'
import { Alert, Input, Button, ButtonGroup } from 'reactstrap'
import { Redirect} from 'react-router'
import ErrorDiv from "../error/error"
import UploadModal from './uploadmodal'
import FilesTable from './filestable'

export default class Upload extends Component {

  constructor(props) {
    super(props)
    this.state = {
      error: false,
      errorMessage: null,
      logged: props.logged,
      user: props.user,
      files: [],
      selected: []
    }
    this.deleteSelectedFiles = this.deleteSelectedFiles.bind(this)
  }

  componentDidMount() {

    let requestUrl = '/api/files'
    axios.get(requestUrl)
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        'files': response.data.files
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        'error': true,
        'errorMessage': error.response.data.errorMessage,
        'status': error.response.status
      })
    })
  }

  deleteSelectedFiles() {
    console.log(this.state.selected)
    let requestUrl = '/api/files/delete'
    let data = {
      filesIdToDelete: this.state.selected
    }
    axios.post(requestUrl, data)
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        files: response.data.files
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        error: true,
        'errorMessage': error.response.data.errorMessage,
        'status': error.response.status
      })
    })
  }

  isDisabled() {
    return this.state.selected.length == 0 ? true : false
  }

  render() {

    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>Upload</h2>
        <hr />
        <UploadModal setStateUpload={p => this.setState(p)} />
        <hr />
        <FilesTable files={this.state.files} setStateUpload={p => this.setState(p)} selected={this.state.selected} />
        <ButtonGroup>
          <Button disabled={this.isDisabled()} onClick={this.deleteSelectedFiles} color="danger"><i class="fas fa-trash-alt"></i> Delete</Button>
          <Button disabled={this.isDisabled()} color="secondary"><i class="fas fa-database"></i> Integrate</Button>
        </ButtonGroup>
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}