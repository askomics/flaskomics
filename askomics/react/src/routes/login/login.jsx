import React, { Component } from 'react'
import axios from 'axios'
import { Button, Form, FormGroup, Label, Input, Alert } from 'reactstrap'
import update from 'immutability-helper'
import { Redirect, Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import ErrorDiv from '../error/error'

export default class Login extends Component {
  constructor (props) {
    super(props)
    this.state = { isLoading: true,
      error: false,
      errorMessage: [],
      login: '',
      password: '',
      logged: false
    }
    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
    this.cancelRequest = null
  }

  handleChange (event) {
    this.setState({
      [event.target.id]: event.target.value
    })
  }

  validateForm () {
    return this.state.login.length > 0 && this.state.password.length > 0
  }

  handleSubmit (event) {
    let requestUrl = '/api/auth/login'
    let data = {
      login: this.state.login,
      password: this.state.password
    }

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          isLoading: false,
          error: response.data.error,
          errorMessage: response.data.errorMessage,
          status: response.status,
          user: response.data.user,
          logged: !response.data.error
        })
        if (!this.state.error) {
          this.props.setStateNavbar({
            config: update(this.props.config, {
              user: {$set: this.state.user},
              logged: {$set: this.state.logged}
            })
          })
        }
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

  componentWillUnmount () {
    if (this.cancelRequest) {
      this.cancelRequest()
    }
  }

  render () {
    let html = <Redirect to="/" />
    if (!this.state.logged) {
      html = (
        <div className="container">
          <h2>Login</h2>
          <hr />
          <div className="col-md-4">
            <Form onSubmit={this.handleSubmit}>
              <FormGroup>
                <Label for="login">Login (username or email)</Label>
                <Input type="text" name="login" id="login" placeholder="login" value={this.state.login} onChange={this.handleChange} />
              </FormGroup>
              <FormGroup>
                <Label for="password">Password</Label>
                <Input type="password" name="password" id="password" placeholder="password" value={this.state.password} onChange={this.handleChange} />
              </FormGroup>
              <Button disabled={!this.validateForm()}>Login</Button>
              <p>(Or <Link to="/signup"> signup</Link>)</p>
            </Form>
            <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
          </div>
        </div>
      )
    }
    return html
  }
}

Login.propTypes = {
  setStateNavbar: PropTypes.func,
  config: PropTypes.object
}
