import React, { Component } from 'react'
import axios from 'axios'
import { Redirect } from 'react-router-dom'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import WaitingDiv from '../../components/waiting'
import { Badge, Button, ButtonGroup } from 'reactstrap'
import FileDownload from 'js-file-download'
import PropTypes from 'prop-types'

export default class ResultsFilesTable extends Component {
  constructor (props) {
    super(props)
    this.state = {
      redirectQueryBuilder: false,
      graphState: []
    }
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
    this.handlePreview = this.handlePreview.bind(this)
    this.handleDownload = this.handleDownload.bind(this)
    this.handleRedo = this.handleRedo.bind(this)
    this.handleEditQuery = this.handleEditQuery.bind(this)
  }

  humanDate (date) {
    let event = new Date(date * 1000)
    return event.toUTCString()
  }

  handleSelection (row, isSelect) {
    if (isSelect) {
      this.props.setStateResults(() => ({
        selected: [...this.props.selected, row.id]
      }))
    } else {
      this.props.setStateResults(() => ({
        selected: this.props.selected.filter(x => x !== row.id)
      }))
    }
  }

  handleSelectionAll (isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStateResults(() => ({
        selected: ids
      }))
    } else {
      this.props.setStateResults(() => ({
        selected: []
      }))
    }
  }

  handlePreview (event) {
    // request api to get a preview of file
    let requestUrl = '/api/results/preview'
    let data = { fileId: event.target.id }
    axios.post(requestUrl, data, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        // set state of resultsPreview
        this.props.setStateResults({
          resultsPreview: response.data.preview,
          headerPreview: response.data.header,
          currentPreview: response.data.id
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          waiting: false
        })
      })
  }

  handleDownload (event) {
    let requestUrl = '/api/results/download'
    let data = { fileId: event.target.id }
    axios.post(requestUrl, data, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then((response) => {
        console.log(requestUrl, response.data)
        FileDownload(response.data, 'result.csv')
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          waiting: false
        })
      })
  }

  handleRedo (event) {
    // request api to get a preview of file
    let requestUrl = '/api/results/graphstate'
    let data = { fileId: event.target.id }
    axios.post(requestUrl, data, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        // set state of resultsPreview
        this.setState({
          redirectQueryBuilder: true,
          graphState: response.data.graphState
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          waiting: false
        })
      })
  }

  handleEditQuery (event) {
    let requestUrl = '/api/results/sparqlquery'
    let data = { fileId: event.target.id }
    axios.post(requestUrl, data, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          redirectSparqlEditor: true,
          sparqlQuery: response.data.query
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          waiting: false
        })
      })
  }

  render () {
    let redirectSparqlEditor
    if (this.state.redirectSparqlEditor) {
      redirectSparqlEditor = <Redirect to={{
        pathname: '/sparql',
        state: {
          redo: true,
          sparqlQuery: this.state.sparqlQuery,
          user: this.props.user,
          logged: this.props.logged
        }
      }} />
    }

    let redirectQueryBuilder
    if (this.state.redirectQueryBuilder) {
      redirectQueryBuilder = <Redirect to={{
        pathname: '/query',
        state: {
          redo: true,
          graphState: this.state.graphState,
          user: this.props.user,
          logged: this.props.logged
        }
      }} />
    }

    let columns = [{
      text: 'Id',
      sort: true,
      formatter: (cell, row) => { return row.id },
      headerStyle: () => { return { width: '5%' } }
    }, {
      dataField: 'start',
      text: 'Creation date',
      sort: true,
      formatter: (cell, row) => { return this.humanDate(cell) }
    }, {
      dataField: 'status',
      text: 'Status',
      formatter: (cell, row) => {
        if (cell == 'started') {
          return <Badge color="info">Started...</Badge>
        }
        if (cell == 'success') {
          return <Badge color="success">Success</Badge>
        }
        if (cell == 'deleting') {
          return <Badge color="warning">Deleting...</Badge>
        }
        return <Badge color="danger">Failure</Badge>
      },
      headerStyle: () => { return { width: '8%' } },
      sort: true
    }, {
      dataField: "nrows",
      text: "Row's number",
      sort: true,
      formatter: (cell, row) => {
        let formattedNrows = new Intl.NumberFormat('fr-FR').format(cell)
        if (cell == this.props.maxRows) {
          return (
            <>{formattedNrows} <i className="fas fa-exclamation-circle"></i></>
          )
        } else {
          return formattedNrows
        }
      },
      headerStyle: () => { return { width: '10%' } }
    }, {
      dataField: 'error_message',
      text: 'Message',
      headerStyle: () => { return { width: '15%' } }
    }, {
      // buttons
      text: 'Actions',
      formatter: (cell, row) => {
        return (
          <ButtonGroup>
            <Button id={row.id} size="sm" outline color="secondary" onClick={this.handlePreview}>Preview</Button>
            <Button id={row.id} size="sm" outline color="secondary" onClick={this.handleDownload}>Download</Button>
            <Button id={row.id} size="sm" outline color="secondary" onClick={this.handleRedo}>Redo</Button>
            <Button id={row.id} size="sm" outline color="secondary" onClick={this.handleEditQuery}>Edit Sparql</Button>
          </ButtonGroup>
        )
      }
    }]

    let defaultSorted = [{
      dataField: 'start',
      order: 'desc'
    }]

    let selectRow = {
      mode: 'checkbox',
      selected: this.props.selected,
      onSelect: this.handleSelection,
      onSelectAll: this.handleSelectionAll
    }

    let noDataIndication = 'No result file'
    if (this.props.waiting) {
      noDataIndication = <WaitingDiv waiting={this.props.waiting} />
    }

    return (
      <div>
        {redirectQueryBuilder}{redirectSparqlEditor}
        <BootstrapTable
          tabIndexCell
          bootstrap4
          keyField='id'
          data={this.props.results}
          columns={columns}
          defaultSorted={defaultSorted}
          pagination={paginationFactory()}
          noDataIndication={noDataIndication}
          selectRow={ selectRow }
        />
      </div>
    )
  }
}

ResultsFilesTable.propTypes = {
  setStateResults: PropTypes.func,
  selected: PropTypes.object,
  user: PropTypes.object,
  logged: PropTypes.bool,
  waiting: PropTypes.bool,
  results: PropTypes.object,
  maxRows: PropTypes.number
}
