import React, { Component } from 'react'
import { Redirect } from 'react-router-dom'
import axios from 'axios'
import { ListGroup, ListGroupItem, Col, Row, Button, ButtonGroup, Form, FormGroup, Label, Input, FormText, InputGroup, InputGroupAddon } from 'reactstrap'
import ErrorDiv from '../error/error'
import PropTypes from 'prop-types'
import update from 'immutability-helper'

export default class DeleteAccount extends Component {
  constructor (props) {
    super(props)
    this.state = {
      confirmDelete: false,
      confirmReset: false,
      redirectAsk: false
    }
    this.toggleDelete = this.toggleDelete.bind(this)
    this.toggleDeleteConfirm = this.toggleDeleteConfirm.bind(this)
    this.cancelRequest
  }

  toggleDeleteConfirm (event) {

    if (event.target.name == "delete") {
      this.setState({
        confirmDelete: event.target.value == "true" ? true : false
      })
    } else {
      this.setState({
        confirmReset: event.target.value == "true" ? true : false
      })
    }
  }

  toggleDelete (event) {

    let requestUrl = '/api/auth/reset_account'
    if (event.target.name == "delete") {
      requestUrl = '/api/auth/delete_account'
    }

    event.persist()

    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          confirmDelete: false,
          confirmReset: false
        })
        if (event.target.name == "delete") {
          this.props.setStateNavbar({
            config: update(this.props.config, {
              user: {$set: {}},
              logged: {$set: false}
            })
          })
          this.setState({
            redirectAsk: true
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

    if (this.state.redirectAsk) {
      return <Redirect to="/" />
    }

    let deleteButton = <Button onClick={this.toggleDeleteConfirm} color="danger" name="delete" value={true}>Delete my account</Button>
    if (this.state.confirmDelete) {
      deleteButton = (
      <ButtonGroup>
        <Button color="secondary" name="delete" onClick={this.toggleDeleteConfirm} value={false}>No</Button>
        <Button color="danger" name="delete" onClick={this.toggleDelete} >Confirm</Button>
      </ButtonGroup>
      )
    }

    let resetButton = <Button onClick={this.toggleDeleteConfirm} color="danger" name="reset" value={true}>Reset my account</Button>
    if (this.state.confirmReset) {
      resetButton = (
      <ButtonGroup>
        <Button color="secondary" name="reset" onClick={this.toggleDeleteConfirm} value={false}>No</Button>
        <Button color="danger" name="reset" onClick={this.toggleDelete} >Confirm</Button>
      </ButtonGroup>
      )
    }

    return (
      <Col md={12}>

      <h4 className="text-danger">Danger zone</h4>
      <ListGroup>
        <ListGroupItem color="danger">
        <Row>
          <Col md={8}>
            <b>Delete your account</b><br />
            Permanently remove user account, uploaded files, datasets and results.
          </Col>
          <Col md={4}>{deleteButton}</Col>
        </Row>
        </ListGroupItem>


        <ListGroupItem color="danger">
        <Row>
          <Col md={8}>
            <b>Reset your account</b><br />
            Permanently remove uploaded files, datasets and results.
          </Col>
          <Col md={4}>{resetButton}</Col>
        </Row>
        </ListGroupItem>

      </ListGroup>
      <br />
      <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </Col>
    )
  }
}

DeleteAccount.propTypes = {
  setStateNavbar: PropTypes.func,
  config: PropTypes.object
}
