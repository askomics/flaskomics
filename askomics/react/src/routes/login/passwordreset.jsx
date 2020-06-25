import React, { Component } from 'react'
import axios from 'axios'
import qs from 'qs'
import { Button, Form, FormGroup, Label, Input, Alert, FormText } from 'reactstrap'
import update from 'immutability-helper'
import { Redirect, Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'

export default class PasswordReset extends Component {
  constructor (props) {
    super(props)
    this.state = {
      token: "",
      username: "",
      fname: "",
      lname: "",
      login: "",
      send: false,
      showResetForm: false,
      redirectLogin: false,
      newPassword: "",
      newPasswordConf: "",
      waiting: true,
      error: false,
      status: 200,
      errorMessage: []
    }
    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
    this.handleSubmitReset = this.handleSubmitReset.bind(this)
    this.cancelRequest = null
  }

  componentWillUnmount () {
    if (this.cancelRequest) {
      this.cancelRequest()
    }
  }

  validateForm () {
    return this.state.login.length > 0
  }

  validatePasswords () {
    return (
      this.state.newPassword.length > 0 &&
      this.state.newPasswordConf == this.state.newPassword
    )
  }

  handleChange (event) {
    this.setState({
      [event.target.id]: event.target.value
    })
  }

  componentDidMount() {
    console.log(this.props)
    if (!this.props.waitForStart) {
      let params = qs.parse(this.props.location.search)
      if ("?token" in params) {
        let token = params["?token"]
        this.checkToken(token)
      } else {
        this.setState({waiting: false})
      }
    }
  }

  handleSubmit (event) {
    // 1st step, send a mail with reset token to the user
    let requestUrl = '/api/auth/reset_password'
    let data = {
      login: this.state.login
    }

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          error: response.data.error,
          errorMessage: response.data.errorMessage,
          status: response.status,
          send: true
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status
        })
      })
    event.preventDefault()
  }

  checkToken(token) {
    // 2nd step, check the token in the link
    let requestUrl = "/api/auth/reset_password"
    let data = {
      token: token
    }
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c })})
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        waiting: false,
        error: response.data.error,
        errorMessage: response.data.errorMessage,
        showResetForm: true,
        token: response.data.token,
        username: response.data.username,
        fname: response.data.fname,
        lname: response.data.lname
      })
    }).catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        waiting: false,
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status
      })
    })
  }


  handleSubmitReset (event) {
    // 3rd step, update the password (and of course check the token)
    let requestUrl = "/api/auth/reset_password"
    let data = {
      token: this.state.token,
      password: this.state.newPassword,
      passwordConf: this.state.newPasswordConf,
    }
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c })})
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        waiting: false,
        error: response.data.error,
        errorMessage: response.data.errorMessage,
        redirectLogin: true,
      })
    }).catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        waiting: false,
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status
      })
    })
    event.preventDefault()
  }

  render () {

    let message = <Alert color="success">Check your email for a link to reset your password. If it doesn’t appear within a few minutes, check your spam folder.</Alert>

    let html = <Redirect to="/" />

    if (this.state.error) {
      return (
        <div className="container">
          <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
        </div>
      )
    }

    if (this.state.waiting) {
      return <WaitingDiv waiting={this.state.waiting} center />
    }

    if (this.state.redirectLogin) {
      return (
        <div className="container">
          <Alert color="success">
            Password updated! <Link to="/login">login</Link>
          </Alert>
        </div>
      )
    }

    if (!this.props.config.logged) {
      // reset form
      if (this.state.showResetForm) {
        html = (
        <div className="container">
          <h2>Reset password</h2>
          <hr />
          <p>Hello {this.state.fname} {this.state.lname}, please enter a new password</p>
          <div className="col-md-4">
            <Form onSubmit={this.handleSubmitReset}>
              <FormGroup>
                <Label for="newPassword">New password</Label>
                <Input type="password" name="newPassword" id="newPassword" placeholder="password" value={this.state.newPassword} onChange={this.handleChange} />
              </FormGroup>
              <FormGroup>
                <Label for="newPasswordConf">Confirmation</Label>
                <Input type="password" name="newPasswordConf" id="newPasswordConf" placeholder="password confirmation" value={this.state.newPasswordConf} onChange={this.handleChange} />
              </FormGroup>
              <Button disabled={!this.validatePasswords()}>Reset</Button>
            </Form>
            <br />
            <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
          </div>
        </div>
        )
      } else {

        // login form to get the token by email
        html = (
          <div className="container">
            <h2>Reset password</h2>
            <hr />
            <div className="col-md-4">
              <Form onSubmit={this.handleSubmit}>
                <FormGroup>
                  <Label for="login">Login (username or email)</Label>
                  <Input type="text" name="login" id="login" placeholder="login" value={this.state.login} onChange={this.handleChange} />
                </FormGroup>
                <Button disabled={!this.validateForm()}>Send reset link</Button>
              </Form>
              <br />
              {this.state.send ? message : null}
            </div>
          </div>
        )
      }
    }
    return html
  }
}

PasswordReset.propTypes = {
  location: PropTypes.object,
  config: PropTypes.object,
  waitForStart: PropTypes.bool
}
