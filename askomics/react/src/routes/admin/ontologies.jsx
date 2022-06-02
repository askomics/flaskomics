import React, { Component } from 'react'
import axios from 'axios'
import {Button, Form, FormGroup, Label, Input, Alert, Row, Col, CustomInput } from 'reactstrap'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'
import { Redirect } from 'react-router-dom'
import WaitingDiv from '../../components/waiting'
import ErrorDiv from '../error/error'

export default class Ontologies extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      error: false,
      errorMessage: '',
      ontologyError: false,
      ontologyErrorMessage: '',
      newontologyError: false,
      newontologyErrorMessage: '',
      ontologies: [],
      datasets: [],
      name: "",
      uri: "",
      shortName: "",
      type: "local",
      datasetId: "",
      label_uri: "rdfs:label",
      ontologiesSelected: []
    }
    this.handleChangeValue = this.handleChangeValue.bind(this)
    this.handleAddOntology = this.handleAddOntology.bind(this)
    this.deleteSelectedOntologies = this.deleteSelectedOntologies.bind(this)
    this.handleOntologySelection = this.handleOntologySelection.bind(this)
    this.handleOntologySelectionAll = this.handleOntologySelectionAll.bind(this)
    this.cancelRequest
  }

  isOntologiesDisabled () {
    return this.state.ontologiesSelected.length == 0
  }

  cleanupOntologies (newOntologies) {
    let cleanOntologies = []
    newOntologies.map(onto => {
      cleanOntologies.push({
          id:onto.id,
          name:onto.name,
          uri:onto.uri,
          short_name: onto.short_name,
          type: onto.type
      })
    })
    return cleanOntologies
  }

  deleteSelectedOntologies () {
    let requestUrl = '/api/admin/delete_ontologies'
    let data = {
      ontologiesIdToDelete: this.state.ontologiesSelected
    }

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          ontologies: response.data.ontologies,
          ontologiesSelected: [],
        })
        this.props.setStateNavbar({
          config: update(this.props.config, {ontologies: {$set: this.cleanupOntologies(response.data.ontologies)}})
        })
      })
  }

  handleChangeValue (event) {
    let data = {}
    data[event.target.id] = event.target.value
    this.setState(data)
  }

  validateOntologyForm () {
    return (
      this.state.name.length > 0 &&
      this.state.uri.length > 0 &&
      this.state.shortName.length > 0 &&
      this.state.datasetId.length > 0
    )
  }

  handleOntologySelection (row, isSelect) {
    if (isSelect) {
      this.setState({
        ontologiesSelected: [...this.state.ontologiesSelected, row.id]
      })
    } else {
      this.setState({
        ontologiesSelected: this.state.ontologiesSelected.filter(x => x !== row.id)
      })
    }
  }

  handleOntologySelectionAll (isSelect, rows) {
    const ontologies = rows.map(r => r.id)
    if (isSelect) {
      this.setState({
        ontologiesSelected: ontologies
      })
    } else {
      this.setState({
        ontologiesSelected: []
      })
    }
  }

  handleAddOntology(event) {

    let requestUrl = "/api/admin/addontology"
    let data = {
      name: this.state.name,
      uri: this.state.uri,
      shortName: this.state.shortName,
      type: this.state.type,
      datasetId: this.state.datasetId,
      label_uri: this.state.label_uri
    }

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      this.setState({
        newontologyError: response.data.error,
        newontologyErrorMessage: [response.data.errorMessage],
        ontologies: response.data.ontologies,
        newontologyStatus: response.status,
        name: "",
        uri: "",
        shortName: "",
        type: "local",
        label_uri: "rdfs:label"
      })
      this.props.setStateNavbar({
        config: update(this.props.config, {ontologies: {$set: this.cleanupOntologies(response.data.ontologies)}})
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        newontologyError: true,
        newontologyErrorMessage: [error.response.data.errorMessage],
        newontologyStatus: error.response.status,
      })
    })
    event.preventDefault()
  }

  componentDidMount () {
    if (!this.props.waitForStart) {
      this.loadOntologies()
      this.loadDatasets()
    }
  }

  loadOntologies() {
    let requestUrl = '/api/admin/getontologies'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        this.setState({
          ontologiesLoading: false,
          ontologies: response.data.ontologies
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          ontologyError: true,
          ontologyErrorMessage: error.response.data.errorMessage,
          ontologyStatus: error.response.status,
          success: !error.response.data.error
        })
      })
  }

  loadDatasets() {
    let requestUrl = '/api/datasets'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        this.setState({
          datasets: response.data.datasets
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
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

    let ontologiesColumns = [{
      editable: false,
      dataField: 'name',
      text: 'Name',
      sort: true
    }, {
      editable: false,
      dataField: 'short_name',
      text: 'Short name',
      sort: true
    }, {
      editable: false,
      dataField: 'uri',
      text: 'Uri',
      sort: true
    }, {
      editable: false,
      dataField: 'dataset_name',
      text: 'Dataset',
      sort: true
    }, {
      editable: false,
      dataField: 'label_uri',
      text: 'Label uri',
      sort: true
  }, {
      editable: false,
      dataField: 'type',
      text: 'Autocomplete type',
      sort: true
    }

  ]

    let ontologiesDefaultSorted = [{
      dataField: 'short_name',
      order: 'asc'
    }]

    let ontologiesSelectRow = {
      mode: 'checkbox',
      clickToSelect: false,
      selected: this.state.ontologiesSelected,
      onSelect: this.handleOntologySelection,
      onSelectAll: this.handleOntologySelectionAll
    }

    let ontologiesNoDataIndication = 'No ontologies'
    if (this.state.ontologiesLoading) {
      ontologiesNoDataIndication = <WaitingDiv waiting={this.state.ontologiesLoading} />
    }

    return (
      <div className="container">
        <h2>Admin</h2>
        <hr />
        <h4>Add a ontology</h4>
        <div>
        <Form onSubmit={this.handleAddOntology}>
          <Row form>
            <Col md={4}>
              <FormGroup>
                <Label for="name">Ontology name</Label>
                <Input type="text" name="name" id="name" placeholder="Ontology name" value={this.state.name} onChange={this.handleChangeValue} />
              </FormGroup>
            </Col>
            <Col md={4}>
              <FormGroup>
                <Label for="shortName">Ontology short name</Label>
                <Input type="text" name="shortName" id="shortName" placeholder="shortName" value={this.state.shortName} onChange={this.handleChangeValue} />
              </FormGroup>
            </Col>
            <Col md={4}>
              <FormGroup>
                <Label for="uri">Ontology uri</Label>
                <Input type="text" name="uri" id="uri" placeholder="uri" value={this.state.uri} onChange={this.handleChangeValue} />
              </FormGroup>
            </Col>
          </Row>
          <Row>
            <Col md={6}>
              <FormGroup>
                <Label for="type">Linked public dataset</Label>
                <CustomInput type="select" name="datasetId" id="datasetId" value={this.state.datasetId} onChange={this.handleChangeValue}>
                  <option value=""></option>
                {this.state.datasets.map(dataset => {
                  if (dataset.public == 1 && dataset.status == "success"){
                    return <option key={dataset.id} value={dataset.id}>{dataset.name}</option>
                  }
                })}
                </CustomInput>
              </FormGroup>
            </Col>
            <Col md={3}>
              <FormGroup>
                <Label for="type">Label uri/Label>
                <Input type="text" name="label_uri" id="label_uri" value={this.state.label_uri} onChange={this.handleChangeValue} />
              </FormGroup>
            </Col>
            <Col md={3}>
              <FormGroup>
                <Label for="type">Autocomplete type</Label>
                <CustomInput type="select" name="type" id="type" value={this.state.type} onChange={this.handleChangeValue}>
                  <option value="none" >none</option>
                  <option value="local" >local</option>
                  <option value="ols" >ols</option>
                </CustomInput>
              </FormGroup>
            </Col>
          </Row>
          <Button disabled={!this.validateOntologyForm()}>Create</Button>
        </Form>
        <br />
        <ErrorDiv status={this.state.newontologyStatus} error={this.state.newontologyError} errorMessage={this.state.newontologyErrorMessage} />
        </div>
        <hr />
        <div className="asko-table-height-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            tabIndexCell
            bootstrap4
            keyField='id'
            data={this.state.ontologies}
            columns={ontologiesColumns}
            defaultSorted={ontologiesDefaultSorted}
            pagination={paginationFactory()}
            noDataIndication={ontologiesNoDataIndication}
            selectRow={ ontologiesSelectRow }
          />
        </div>
        <br />
        <Button disabled={this.isOntologiesDisabled()} onClick={this.deleteSelectedOntologies} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
        <ErrorDiv status={this.state.ontologyStatus} error={this.state.ontologyError} errorMessage={this.state.ontologyErrorMessage} />
      </div>
    )
  }
}

Ontologies.propTypes = {
  setStateNavbar: PropTypes.func,
  waitForStart: PropTypes.bool,
  config: PropTypes.object
}
