import React, { Component } from 'react'
import axios from 'axios'
import { Redirect } from 'react-router-dom'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import cellEditFactory from 'react-bootstrap-table2-editor'
import WaitingDiv from '../../components/waiting'
import Utils from '../../classes/utils'
import { Badge, Button, ButtonGroup, FormGroup, CustomInput, Input, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import FileDownload from 'js-file-download'
import PropTypes from 'prop-types'
import ErrorDiv from '../error/error'
import SyntaxHighlighter from 'react-syntax-highlighter'
import { monokai } from 'react-syntax-highlighter/dist/esm/styles/hljs'

export default class ResultsFilesTable extends Component {
  constructor (props) {
    super(props)
    this.state = {
      redirectQueryBuilder: false,
      graphState: [],
      modal: false,
      idToPublish: null,
      description: '',
      error: false,
      errorMessage: null,
      status: null,
      modalTracebackTitle: "",
      modalTracebackContent: "",
      modalTraceback: false
    }
    this.utils = new Utils()
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
    this.handlePreview = this.handlePreview.bind(this)
    this.handleDownload = this.handleDownload.bind(this)
    this.handleRedo = this.handleRedo.bind(this)
    this.handleEditQuery = this.handleEditQuery.bind(this)
    this.handleSendToGalaxy = this.handleSendToGalaxy.bind(this)
    this.togglePublicQuery = this.togglePublicQuery.bind(this)
    this.handleClickError = this.handleClickError.bind(this)
    this.toggleModalTraceback = this.toggleModalTraceback.bind(this)
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
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        redirectSparqlEditor: true,
        sparqlQuery: response.data.query,
        graphs: response.data.graphs,
        endpoints: response.data.endpoints,
        diskSpace: response.data.diskSpace
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

  handleSendToGalaxy (event) {
    let requestUrl = '/api/results/send2galaxy'
    let data = {fileId: event.target.id, fileToSend: event.target.name}
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      console.log(requestUrl, response.data)
    })
    .catch(error => {
      console.log(error)
    })
  }

  togglePublicQuery(event) {
    // Unpublish
    this.setState({
      idToPublish: event.target.id,
      newPublishStatus: event.target.value == 1 ? false : true,
      description: ''
    }, () => {
      this.publish()
    })
  }

  publish() {
    let requestUrl = '/api/results/publish'
    let data = {
      id: this.state.idToPublish,
      public: this.state.newPublishStatus
    }
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      this.setState({
        modal: false,
        idToPublish: null
      })
      this.props.setStateResults({
        results: response.data.files,
        waiting: false
      })
    })
    .catch(error => {
      this.setState({
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status,
        waiting: false
      })
    })
  }

  saveNewDescription (oldValue, newValue, row) {

    if (newValue === oldValue) {return}

    let requestUrl = '/api/results/description'
    let data = {
      id: row.id,
      newDesc: newValue
    }
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      this.props.setStateResults({
        results: response.data.files,
        waiting: false
      })
    })
    .catch(error => {
      this.setState({
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status,
        waiting: false
      })
    })
  }

  handleClickError(event) {
    console.log(event.target.id)

    this.props.results.forEach(result => {
      if (result.id == event.target.id) {
        this.setState({
          modalTracebackTitle: result.errorMessage ? result.errorMessage : "Internal server error",
          modalTracebackContent: result.traceback ? result.traceback : "Internal server error",
          modalTraceback: true
        })
      }
    })
  }

  toggleModalTraceback () {
    this.setState({
      modalTraceback: !this.state.modalTraceback
    })
  }

  render () {
    let redirectSparqlEditor
    if (this.state.redirectSparqlEditor) {
      redirectSparqlEditor = <Redirect to={{
        pathname: '/sparql',
        state: {
          diskSpace: this.state.diskSpace,
          sparqlQuery: this.state.sparqlQuery,
          graphs: this.state.graphs,
          endpoints: this.state.endpoints,
          config: this.props.config
        }
      }} />
    }

    let redirectQueryBuilder
    if (this.state.redirectQueryBuilder) {
      redirectQueryBuilder = <Redirect to={{
        pathname: '/query',
        state: {
          redo: true,
          config: this.props.config,
          graphState: this.state.graphState
        }
      }} />
    }

    let columns = [{
      dataField: 'id',
      text: 'Id',
      sort: true,
      formatter: (cell, row) => { return row.id },
      editable: false
    }, {
      dataField: 'description',
      text: 'Description',
      sort: true
    }, {
      dataField: 'start',
      text: 'Creation date',
      sort: true,
      formatter: (cell, row) => { return this.utils.humanDate(cell) },
      editable: false
    }, {
      dataField: 'public',
      text: 'Public',
      sort: true,
      hidden: this.props.config.user.admin === 1 ? false : true,
      formatter: (cell, row) => {
        return (
          <FormGroup>
            <div>
              <CustomInput disabled={row.status == "success" ? false : true} type="switch" id={row.id} onChange={this.togglePublicQuery} checked={cell} value={cell} />
            </div>
          </FormGroup>
        )
      },
      editable: false
    }, {
      dataField: 'status',
      text: 'Status',
      formatter: (cell, row) => {
        if (cell == 'queued') {
          return <Badge color="secondary">Queued</Badge>
        }
        if (cell == 'started') {
          return <Badge color="info">Started</Badge>
        }
        if (cell == 'success') {
          return <Badge color="success">Success</Badge>
        }
        if (cell == 'deleting') {
          return <Badge color="warning">Deleting...</Badge>
        }
        return <Badge style={{cursor: "pointer"}} id={row.id} color="danger" onClick={this.handleClickError}>Failure</Badge>
      },
      sort: true,
      editable: false
    }, {
      dataField: "nrows",
      text: "Rows",
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
      editable: false
    }, {
      dataField: "size",
      text: "Size",
      sort: true,
      formatter: (cell, row) => {
        return cell ? this.utils.humanFileSize(cell, true) : ''
      },
      editable: false
    }, {
      // buttons
      dataField: "end", // FIXME: we don't need end dataField, but dataField have to be set
      text: 'Actions',
      formatter: (cell, row) => {
        return (
          <ButtonGroup>
            <Button disabled={row.status == "success" ? false : true} id={row.id} size="sm" outline color="secondary" onClick={this.handlePreview}>Preview</Button>
            <Button disabled={row.status == "success" ? false : true} id={row.id} size="sm" outline color="secondary" onClick={this.handleDownload}>Download</Button>
            <Button disabled={row.sparqlQuery != null ? true : false} id={row.id} size="sm" outline color="secondary" onClick={this.handleRedo}>Redo</Button>
            <Button id={row.id} size="sm" outline color="secondary" onClick={this.handleEditQuery}>Sparql</Button>
            {this.props.config.user.galaxy ? <Button disabled={row.status == "success" ? false : true} name="result" id={row.id} size="sm" outline color="secondary" onClick={this.handleSendToGalaxy}>Send result to Galaxy</Button> : null}
            {this.props.config.user.galaxy ? <Button disabled={row.sparqlQuery != null ? true : false} name="query" id={row.id} size="sm" outline color="secondary" onClick={this.handleSendToGalaxy}>Send query to Galaxy</Button> : null}
          </ButtonGroup>
        )
      },
      editable: false
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
        <div className="asko-table-height-div">
          {redirectQueryBuilder}{redirectSparqlEditor}
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            tabIndexCell
            bootstrap4
            keyField='id'
            data={this.props.results}
            columns={columns}
            defaultSorted={defaultSorted}
            pagination={paginationFactory()}
            noDataIndication={noDataIndication}
            selectRow={ selectRow }
            cellEdit={ cellEditFactory({
              mode: 'click',
              beforeSaveCell: (oldValue, newValue, row) => { this.saveNewDescription(oldValue, newValue, row) },
            })}
          />
        </div>

        <Modal size="lg" isOpen={this.state.modalTraceback} toggle={this.toggleModalTraceback}>
          <ModalHeader toggle={this.toggleModalTraceback}>{this.state.modalTracebackTitle.substring(0, 100)}</ModalHeader>
          <ModalBody>
            <div>
              <SyntaxHighlighter language="python" style={monokai}>
                {this.state.modalTracebackContent}
              </SyntaxHighlighter>
            </div>
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModalTraceback  }>Close</Button>
          </ModalFooter>
        </Modal>
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>

    )
  }
}

ResultsFilesTable.propTypes = {
  setStateResults: PropTypes.func,
  selected: PropTypes.array,
  waiting: PropTypes.bool,
  results: PropTypes.array,
  config: PropTypes.object,
  maxRows: PropTypes.number
}
