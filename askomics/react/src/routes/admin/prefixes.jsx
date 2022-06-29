import React, { Component } from 'react'
import axios from 'axios'
import {Button, Form, FormGroup, Label, Input, Alert, Row, Col, CustomInput } from 'reactstrap'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'
import { Redirect } from 'react-router-dom'
import WaitingDiv from '../../components/waiting'
import ErrorDiv from '../error/error'

export default class Prefixes extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      error: false,
      errorMessage: '',
      prefixError: false,
      prefixErrorMessage: '',
      newprefixError: false,
      newprefixErrorMessage: '',
      prefixes: [],
      prefix: "",
      namespace: "",
      prefixesSelected: []
    }
    this.handleChangePrefix = this.handleChangePrefix.bind(this)
    this.handleChangeNamespace = this.handleChangeNamespace.bind(this)
    this.handleAddPrefix = this.handleAddPrefix.bind(this)
    this.deleteSelectedPrefixes = this.deleteSelectedPrefixes.bind(this)
    this.handlePrefixSelection = this.handlePrefixSelection.bind(this)
    this.handlePrefixSelectionAll = this.handlePrefixSelectionAll.bind(this)
    this.cancelRequest
  }

  isPrefixesDisabled () {
    return this.state.prefixesSelected.length == 0
  }

  deleteSelectedPrefixes () {
    let requestUrl = '/api/admin/delete_prefixes'
    let data = {
      prefixesIdToDelete: this.state.prefixesSelected
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          prefixes: response.data.prefixes,
          prefixesSelected: [],
        })
      })
  }

  handleChangePrefix (event) {
    this.setState({
      prefix: event.target.value
    })
  }

  handleChangeNamespace (event) {
    this.setState({
      namespace: event.target.value
    })
  }

  validatePrefixForm () {
    return (
      this.state.prefix.length > 0 &&
      this.state.namespace.length > 0
    )
  }

  handlePrefixSelection (row, isSelect) {
    if (isSelect) {
      this.setState({
        prefixesSelected: [...this.state.prefixesSelected, row.id]
      })
    } else {
      this.setState({
        prefixesSelected: this.state.prefixesSelected.filter(x => x !== row.id)
      })
    }
  }

  handlePrefixSelectionAll (isSelect, rows) {
    const prefixes = rows.map(r => r.id)
    if (isSelect) {
      this.setState({
        prefixesSelected: prefixes
      })
    } else {
      this.setState({
        prefixesSelected: []
      })
    }
  }

  handleAddPrefix(event) {

    let requestUrl = "/api/admin/addprefix"
    let data = {
      prefix: this.state.prefix,
      namespace: this.state.namespace,
    }

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        newprefixError: response.data.error,
        newprefixErrorMessage: response.data.errorMessage,
        prefixes: response.data.prefixes,
        newprefixStatus: response.status,
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        newprefixError: true,
        newprefixErrorMessage: error.response.data.errorMessage,
        newprefixStatus: error.response.status,
      })
    })
    event.preventDefault()
  }

  componentDidMount () {
    if (!this.props.waitForStart) {
      this.loadPrefixes()
    }
  }

  loadPrefixes() {
    let requestUrl = '/api/admin/getprefixes'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        this.setState({
          prefixesLoading: false,
          prefixes: response.data.prefixes
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          prefixError: true,
          prefixErrorMessage: error.response.data.errorMessage,
          prefixStatus: error.response.status,
          success: !error.response.data.error
        })
      })
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  render () {

    if (!this.props.waitForStart && !this.props.config.logged) {
      return <Redirect to="/login" />
    }
    if (!this.props.waitForStart && this.props.config.user.admin != 1) {
      return <Redirect to="/" />
    }

    if (this.props.waitForStart) {
      return <WaitingDiv waiting={this.props.waitForStart} center />
    }

    let prefixesColumns = [{
      editable: false,
      dataField: 'prefix',
      text: 'Prefix',
      sort: true
    }, {
      editable: false,
      dataField: 'namespace',
      text: 'Namespace',
      sort: true
    }]

    let prefixesDefaultSorted = [{
      dataField: 'prefix',
      order: 'asc'
    }]

    let prefixesSelectRow = {
      mode: 'checkbox',
      clickToSelect: false,
      selected: this.state.prefixesSelected,
      onSelect: this.handlePrefixSelection,
      onSelectAll: this.handlePrefixSelectionAll
    }

    let prefixesNoDataIndication = 'No custom prefixes'
    if (this.state.prefixesLoading) {
      prefixesNoDataIndication = <WaitingDiv waiting={this.state.prefixesLoading} />
    }

    return (
      <div className="container">
        <h2>Admin</h2>
        <hr />
        <h4>Add a prefix</h4>
        <div>
        <Form onSubmit={this.handleAddPrefix}>
          <Row form>
            <Col md={6}>
              <FormGroup>
                <Label for="fname">Prefix</Label>
                <Input type="text" name="prefix" id="prefix" placeholder="prefix" value={this.state.prefix} onChange={this.handleChangePrefix} />
              </FormGroup>
            </Col>
            <Col md={6}>
              <FormGroup>
                <Label for="lname">Namespace</Label>
                <Input type="text" name="namespace" id="namespace" placeholder="namespace" value={this.state.namespace} onChange={this.handleChangeNamespace} />
              </FormGroup>
            </Col>
          </Row>
          <Button disabled={!this.validatePrefixForm()}>Create</Button>
        </Form>
        <ErrorDiv status={this.state.newprefixstatus} error={this.state.newprefixerror} errorMessage={this.state.newprefixerrorMessage} />
        <br />
        </div>
        <hr />
        <div className="asko-table-height-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            tabIndexCell
            bootstrap4
            keyField='id'
            data={this.state.prefixes}
            columns={prefixesColumns}
            defaultSorted={prefixesDefaultSorted}
            pagination={paginationFactory()}
            noDataIndication={prefixesNoDataIndication}
            selectRow={ prefixesSelectRow }
          />
        </div>
        <br />
        <Button disabled={this.isPrefixesDisabled()} onClick={this.deleteSelectedPrefixes} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
        <ErrorDiv status={this.state.prefixStatus} error={this.state.prefixError} errorMessage={this.state.prefixErrorMessage} />
      </div>
    )
  }
}

Prefixes.propTypes = {
  waitForStart: PropTypes.bool,
  config: PropTypes.object
}
