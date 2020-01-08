import React, { Component } from 'react'
import axios from 'axios'
import { Col, Row, Button, Form, FormGroup, Label, Input, FormText } from 'reactstrap'
import ErrorDiv from '../error/error'
import PropTypes from 'prop-types'
import update from 'immutability-helper'

export default class UpdateProfile extends Component {
  constructor (props) {
    super(props)
    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
    this.state = {
      newFname: '',
      newLname: '',
      newEmail: ''
    }
    this.cancelRequest
  }

  handleChange (event) {
    this.setState({
      [event.target.id]: event.target.value
    })
  }

  validateEmail (email) {
    let re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    return re.test(String(email).toLowerCase())
  }

  validateForm () {
    return (
      (this.state.newFname.length > 0 || this.state.newLname.length > 0 || this.validateEmail(this.state.newEmail)) &&
      (this.validateEmail(this.state.newEmail) || this.state.newEmail.length == 0)
    )
  }

  handleSubmit (event) {
    let requestUrl = '/api/auth/profile'
    let data = {
      newFname: this.state.newFname,
      newLname: this.state.newLname,
      newEmail: this.state.newEmail
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
          status: response.data.error ? 500 : 200
        })
        if (!this.state.error) {
          this.props.setStateNavbar({
            config: update(this.props.config, {user: {$set: this.state.user}})
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

  render () {
    let successTick
    if (this.state.success) {
      successTick = <i color="success" className="fas fa-check"></i>
    }

    return (
      <Col md={4}>
        <h4>Update profile</h4>
        <Form onSubmit={this.handleSubmit}>
          <Row form>
            <Col md={6}>
              <FormGroup>
                <Label for="fname">First name</Label>
                <Input type="text" name="fname" id="newFname" placeholder={this.props.config.user.fname} value={this.state.newFname} onChange={this.handleChange} />
              </FormGroup>
            </Col>
            <Col md={6}>
              <FormGroup>
                <Label for="lname">Last name</Label>
                <Input type="text" name="lname" id="newLname" placeholder={this.props.config.user.lname} value={this.state.newLname} onChange={this.handleChange} />
              </FormGroup>
            </Col>
          </Row>
          <FormGroup>
            <Label for="email">Email</Label>
            <Input type="email" name="email" id="newEmail" placeholder={this.props.config.user.email} value={this.state.newEmail} onChange={this.handleChange} />
          </FormGroup>
          <Button disabled={!this.validateForm()}>Update profile {successTick}</Button>
        </Form>
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </Col>
    )
  }
}

UpdateProfile.propTypes = {
  setStateNavbar: PropTypes.func,
  config: PropTypes.object
}
