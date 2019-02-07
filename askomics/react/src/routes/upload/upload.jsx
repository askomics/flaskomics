import React, { Component } from "react"
import axios from 'axios'
import { Alert } from 'reactstrap';
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
      files: []
    }
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

  render() {

    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    let errorDiv
    if (this.state.error) {
      errorDiv = (
        <div>
          <Alert color="danger">
            <i className="fas fa-exclamation-circle"></i> {this.state.errorMessage}
          </Alert>
        </div>
      )
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>Upload</h2>
        <hr />
        <UploadModal setStateUpload={p => this.setState(p)} />
        <hr />
        <FilesTable files={this.state.files} />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}