import React, { Component } from "react"
import axios from 'axios'
import { Col, Row, Button, Form, FormGroup, Label, Input, FormText } from 'reactstrap'
import ErrorDiv from "../error/error"

export default class UpdateApiKey extends Component {

  constructor(props) {
    super(props)
    this.state = {}
    this.handleSubmit = this.handleSubmit.bind(this)
  }

  handleSubmit(event) {

    let requestUrl = '/api/update_apikey'

    axios.get(requestUrl)
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        isLoading: false,
        error: response.data.error,
        errorMessage: response.data.errorMessage,
        user: response.data.user,
        success: !response.data.error,
      })
      if (!this.state.error) {
        this.props.setStateNavbar({
          user: this.state.user,
          logged: true
        })
      }
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status,
        success: !response.data.error,
      })
    })
    event.preventDefault()
  }

  render() {
    let successTick
    if (this.state.success) {
      successTick = <i color="success" className="fas fa-check"></i>
    }

    return (
      <Col md={4}>
      <h4>Update api key</h4>
        <Form onSubmit={this.handleSubmit}>
          <Row form>
          </Row>
          <FormGroup>
            <Label for="apikey">Api key</Label>
            <Input type="apikey" name="apikey" id="apikey" value={this.props.user.apikey} disabled />
          </FormGroup>
          <Button >Update api key {successTick}</Button>
        </Form>
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </Col>
    )
  }
}

