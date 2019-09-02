import React, { Component } from 'react'
import { Form, FormGroup, FormText, Label, Input, Button, CustomInput, Progress } from 'reactstrap'
import axios from 'axios'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import WaitingDiv from '../../components/waiting'
import AskoContext from '../../components/context'

export default class UploadGalaxyForm extends Component {
  static contextType = AskoContext
  constructor (props) {
    super(props)
    this.state = {
      selected: [],
      disabled: false,
      waiting: true
    }


    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
    this.cancelRequest
  }

  componentDidMount () {

    let requestUrl = '/api/galaxy/datasets'
    axios.get(requestUrl, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
    axios.post(requestUrl, data, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
    console.log("upload", this.state.selected)
    let data = {datasets_id: this.state.selected}
    let requestUrl = '/api/galaxy/upload_datasets'
    axios.post(requestUrl, data, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      console.log(requestUrl, response.data)
      let requestUrlFiles = '/api/files'
      axios.get(requestUrlFiles, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
    if (isSelect) {
      this.setState(() => ({
        selected: [...this.state.selected, row.dataset_id]
      }))
    } else {
      this.setState(() => ({
        selected: this.state.selected.filter(x => x !== row.dataset_id)
      }))
    }
  }

  handleSelectionAll (isSelect, rows) {
    const ids = rows.map(r => r.dataset_id)
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
      text: 'Dataset name',
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
      mode: 'checkbox',
      selected: this.state.selected,
      onSelect: this.handleSelection,
      onSelectAll: this.handleSelectionAll
    }

    let noDataIndication = 'No dataset in this history'
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
            keyField='dataset_id'
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

    return (
      <div>
        <br />
        <center>
          <WaitingDiv waiting={this.state.waiting} />
        </center>
        {historyForm}
        {DatasetsTable}
        <Button disabled={this.state.selected.length > 0 ? false : true} onClick={this.handleSubmit} color="secondary">Upload</Button>
      </div>
    )
  }
}

UploadGalaxyForm.propTypes = {
  setStateUpload: PropTypes.func,
  waiting: PropTypes.bool
}
