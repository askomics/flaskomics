import React, { Component } from "react"
import axios from 'axios'
import { Alert } from 'reactstrap';
import { Redirect} from 'react-router'
import ErrorDiv from "../error/error"

export default class Ask extends Component {

  constructor(props) {
    super(props)
    this.state = {
      waiting: true,
      error: false,
      errorMessage: null,
      logged: props.logged,
      user: props.user
    }
    this.cancelRequest
  }

  componentDidMount() {

    let requestUrl = '/api/hello'
    axios.get(requestUrl, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        message: response.data.message,
        waiting: false
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        waiting: false,
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status
      })
    })
  }

  componentWillUnmount() {
    this.cancelRequest()
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

    let waitingDiv
    if (this.state.waiting) {
      waitingDiv = (
        <div>
          <i className="fas fa-spinner fa-spin"></i>
        </div>
      )
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>Ask!</h2>
        <hr />
        {waitingDiv}
        <p>{this.state.message}</p>
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}