import React, { Component } from 'react'
import axios from 'axios'
import { Col, Button, Form, FormGroup, Label, Input, FormText, InputGroup, InputGroupAddon } from 'reactstrap'
import ErrorDiv from '../error/error'
import PropTypes from 'prop-types'
import update from 'immutability-helper'

export default class UpdateApiKey extends Component {
  constructor (props) {
    super(props)
    this.state = {}
    this.handleSubmit = this.handleSubmit.bind(this)
    this.cancelRequest
  }

  handleSubmit (event) {
    let requestUrl = '/api/auth/apikey'

    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
        <h4>Manage API key</h4>
        <Form onSubmit={this.handleSubmit}>
          <InputGroup>
            <Input value={this.props.config.user.apikey} />
            <InputGroupAddon addonType="append">
              <Button >Create new</Button>
            </InputGroupAddon>
          </InputGroup>
        </Form>
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </Col>
    )
  }
}

UpdateApiKey.propTypes = {
  setStateNavbar: PropTypes.func,
  config: PropTypes.object
}
