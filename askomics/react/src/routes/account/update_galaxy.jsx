import React, { Component } from 'react'
import axios from 'axios'
import { Col, Row, Button, Form, FormGroup, Label, Input, FormText } from 'reactstrap'
import ErrorDiv from '../error/error'
import PropTypes from 'prop-types'
import AskoContext from '../../components/context'

export default class UpdateGalaxyAccount extends Component {
  static contextType = AskoContext
  constructor (props) {
    super(props)
    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
    this.state = {
      gurl: '',
      gkey: ''
    }
    this.cancelRequest
  }

  handleChange (event) {
    this.setState({
      [event.target.id]: event.target.value
    })
  }

  isUrl(s) {
     var regexp = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/
     return regexp.test(s);
  }

  validateForm () {
    return (
      (this.isUrl(this.state.gurl) && this.state.gkey.length > 0)
    )
  }

  handleSubmit (event) {
    let requestUrl = '/api/auth/galaxy'
    let data = {
      gurl: this.state.gurl,
      gkey: this.state.gkey
    }

    axios.post(requestUrl, data, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          isLoading: false,
          error: response.data.error,
          errorMessage: response.data.errorMessage,
          user: response.data.user,
          success: !response.data.error
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
        <h4>Connect a Galaxy account</h4>
        <Form onSubmit={this.handleSubmit}>
          <FormGroup>
            <Label for="fname">Galaxy URL</Label>
            <Input type="url" name="gurl" id="gurl" placeholder={this.props.user.galaxy ? this.props.user.galaxy.url : "Enter a Galaxy URL"} value={this.state.gurl} onChange={this.handleChange} />
          </FormGroup>
          <FormGroup>
            <Label for="lname">Galaxy API key</Label>
            <Input type="text" name="gkey" id="gkey" placeholder={this.props.user.galaxy ? this.props.user.galaxy.key : "Enter a Galaxy API key"} value={this.state.gkey} onChange={this.handleChange} />
          </FormGroup>
          <Button disabled={!this.validateForm()}>Update Galaxy account {successTick}</Button>
        </Form>
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </Col>
    )
  }
}

UpdateGalaxyAccount.propTypes = {
  setStateNavbar: PropTypes.func,
  user: PropTypes.object
}
