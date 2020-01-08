import React, { Component } from 'react'
import axios from 'axios'
import { Col, Row, Button, Form, FormGroup, Label, Input, FormText, Alert } from 'reactstrap'
import ErrorDiv from '../error/error'
import PropTypes from 'prop-types'

export default class UpdatePassword extends Component {
  constructor (props) {
    super(props)
    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
    this.state = {
      oldPassword: '',
      newPassword: '',
      confPassword: ''
    }
    this.cancelRequest
  }

  handleChange (event) {
    this.setState({
      [event.target.id]: event.target.value
    })
  }

  validateForm () {
    return (
      this.state.oldPassword.length > 0 &&
      this.state.newPassword.length > 0 &&
      this.state.newPassword == this.state.confPassword &&
      this.state.newpassword != this.state.oldPassword
    )
  }

  handleSubmit (event) {
    let requestUrl = '/api/auth/password'
    let data = {
      oldPassword: this.state.oldPassword,
      newPassword: this.state.newPassword,
      confPassword: this.state.confPassword
    }

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          isLoading: false,
          error: response.data.error,
          errorMessage: response.data.errorMessage,
          user: response.data.user,
          success: !response.data.error,
          status: response.data.error ? 500 : 200,
          oldPassword: '',
          newPassword: '',
          confPassword: ''
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          success: !response.data.error,
          oldPassword: '',
          newPassword: '',
          confPassword: ''
        })
      })
    event.preventDefault()
  }

  render () {
    let successTick
    if (this.state.success) {
      successTick = <i color="success" className="fas fa-check"></i>
    }
    return (
      <Col md={4}>
        <h4>Update password</h4>
        <Form onSubmit={this.handleSubmit}>
          <Row form>
          </Row>
          <FormGroup>
            <Label for="oldpassword">Old Password</Label>
            <Input type="password" name="oldpassword" id="oldPassword" placeholder="old password" value={this.state.oldPassword} onChange={this.handleChange} />
          </FormGroup>
          <FormGroup>
            <Label for="newpassword">New Password</Label>
            <Input type="password" name="newpassword" id="newPassword" placeholder="new password" value={this.state.newPassword} onChange={this.handleChange} />
          </FormGroup>
          <FormGroup>
            <Label for="confpassword">Confirm new Password</Label>
            <Input type="password" name="confpassword" id="confPassword" placeholder="confirm new password" value={this.state.confPassword} onChange={this.handleChange} />
          </FormGroup>
          <Button disabled={!this.validateForm()}>Update password {successTick}</Button>
        </Form>
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </Col>
    )
  }
}

UpdatePassword.propTypes = {
  setStateNavbar: PropTypes.func,
  config: PropTypes.object
}
