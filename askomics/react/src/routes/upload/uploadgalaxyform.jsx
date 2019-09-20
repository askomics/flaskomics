import React, { Component } from 'react'
import { Form, FormGroup, FormText, Label, Input, Button, CustomInput, Progress } from 'reactstrap'
import axios from 'axios'
import { Redirect } from 'react-router-dom'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import WaitingDiv from '../../components/waiting'

export default class UploadGalaxyForm extends Component {
  constructor (props) {
    super(props)
    this.state = {
      selected: [],
      disabled: false,
      waiting: true,
      uploading: false
    }

    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
    this.cancelRequest
  }

  componentDidMount () {
    let requestUrl = '/api/galaxy/datasets'
    if (this.props.getQueries) {
      requestUrl = '/api/galaxy/queries'
    }
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          waiting: false,
          datasets: response.data.datasets,
          histories: response.data.histories
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          waiting: false
        })
      })
  }


  handleChange (event) {
    this.setState({
      waiting: true
    })
    let data = {history_id: event.target.value}
    let requestUrl = '/api/galaxy/datasets'
    if (this.props.getQueries) {
      requestUrl = '/api/galaxy/queries'
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        waiting: false,
        datasets: response.data.datasets,
        histories: response.data.histories
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        error: true,
        waiting: false
      })
    })

  }

  handleSubmit (event) {
    if (this.props.getQueries) {
      this.handleSubmitQuery (event)
    } else {
      this.handleSubmitUpload(event)
    }
  }


  handleSubmitQuery (event) {
    let requestUrl = '/api/galaxy/getdatasetcontent'
    let data = {dataset_id: this.state.selected[0]}
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          redirectQueryBuilder: true,
          graphState: response.data.dataset_content
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



  handleSubmitUpload (event) {
    this.setState({
      uploading: true,
      selected: []
    })
    let data = {datasets_id: this.state.selected}
    let requestUrl = '/api/galaxy/upload_datasets'
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      this.setState({
        uploading: false
      })
      console.log(requestUrl, response.data)
      let requestUrlFiles = '/api/files'
      axios.get(requestUrlFiles, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
          console.log(requestUrlFiles, response.data)
          this.props.setStateUpload({
            files: response.data.files
          })
        })
        .catch(error => {
          console.log(error, error.response.data.errorMessage)
        })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        error: true,
        waiting: false
      })
    })

  }



  handleSelection (row, isSelect) {
    console.log("handle selection")
    if (isSelect) {
      this.setState(() => ({
        selected: [...this.state.selected, row.id]
      }))
    } else {
      this.setState(() => ({
        selected: this.state.selected.filter(x => x !== row.id)
      }))
    }
  }

  handleSelectionAll (isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.setState(() => ({
        selected: ids
      }))
    } else {
      this.setState(() => ({
        selected: []
      }))
    }
  }

  render () {

    let columns = [{
      dataField: 'name',
      text: this.props.getQueries ? 'Query name' : 'Dataset name',
      sort: true
    }, {
      dataField: 'extension',
      text: 'Type',
      sort: true
    }]

    let defaultSorted = [{
      dataField: 'create_time',
      order: 'desc'
    }]

    let selectRow = {
      mode: this.props.getQueries ? 'radio' : 'checkbox',
      selected: this.state.selected,
      onSelect: this.handleSelection,
      onSelectAll: this.handleSelectionAll
    }

    let noDataIndication = this.props.getQueries ? 'No AskOmics queries in this history' : 'No dataset in this history'
    if (this.props.waiting) {
      noDataIndication = <WaitingDiv waiting={this.state.waiting} />
    }

    let historyForm
    let DatasetsTable
    if (!this.state.waiting) {
      historyForm = (
        <div>
          <FormGroup>
            <Label for="histories">Select a galaxy history</Label>
            <CustomInput onChange={this.handleChange} type="select" id="histories" name="histories">
            {this.state.histories.map((history, index) => (
              <option key={index} value={history.id} history_id={history.id} selected={history.selected}>{history.name}</option>
            ))}
            </CustomInput>
          </FormGroup>
        </div>
      )
      DatasetsTable = (
        <div>
          <BootstrapTable
            tabIndexCell
            bootstrap4
            keyField='id'
            data={this.state.datasets}
            columns={columns}
            defaultSorted={defaultSorted}
            pagination={paginationFactory()}
            noDataIndication={noDataIndication}
            selectRow={ selectRow }
          />
        </div>
      )
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

    return (
      <div>
        {redirectQueryBuilder}
        <br />
        <center>
          <WaitingDiv waiting={this.state.waiting} />
        </center>
        {historyForm}
        {DatasetsTable}
        <div className="clearfix">
          <Button className="float-left" disabled={this.state.selected.length > 0 ? false : true} onClick={this.handleSubmit} color="secondary">
            {this.props.getQueries ? 'Start query' : 'Upload'}
          </Button>
          <WaitingDiv className="float-right" waiting={this.state.uploading} size='xm' />
        </div>
      </div>
    )
  }
}

UploadGalaxyForm.propTypes = {
  setStateUpload: PropTypes.func,
  waiting: PropTypes.bool,
  getQueries: PropTypes.bool,
  config: PropTypes.object
}
