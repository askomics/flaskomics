import React, { Component } from "react"
import axios from 'axios'
import { Alert } from 'reactstrap';
import { Redirect} from 'react-router'
import ErrorDiv from "../error/error"

export default class Ask extends Component {

  constructor(props) {
    super(props)
    this.state = {
      error: false,
      errorMessage: null,
      logged: props.logged,
      user: props.user
    }
  }

  componentDidMount() {

    let requestUrl = '/api/hello'
    axios.get(requestUrl)
    .then(response => {
      console.log('Ask', requestUrl, response.data)
      this.setState({
        'message': response.data.message
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
        <h2>Ask!</h2>
        <hr />
        <p>{this.state.message}</p>
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}