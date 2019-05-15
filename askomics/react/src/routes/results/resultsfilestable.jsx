import React, { Component } from "react"
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import WaitingDiv from "../../components/waiting"
import { Badge, Button } from 'reactstrap'

export default class ResultsFilesTable extends Component {


  constructor(props) {
    super(props)
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
    this.handlePreview = this.handlePreview.bind(this)
    this.handleDownload = this.handleDownload.bind(this)
    this.handleRedo = this.handleRedo.bind(this)
  }

  humanDate(date) {
    let event = new Date(date * 1000)
    return event.toUTCString()
  }

  handleSelection(row, isSelect) {
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

  handleSelectionAll(isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStateResults(() => ({
        selected: ids
      }));
    } else {
      this.props.setStateResults(() => ({
        selected: []
      }))
    }
  }

  handlePreview(event) {
    // request api to get a preview of file
    let requestUrl = '/api/results/preview'
    let data = {fileId: event.target.id}
    axios.post(requestUrl, data, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
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

  handleDownload(event) {
    console.log(event.target.id)
  }

  handleRedo(event) {
    console.log(event.target.id)
  }


  render() {

    let columns = [{
      text: 'Id',
      sort: true,
      formatter: (cell, row) => {return row.id},
      headerStyle: () => {return { width: "10%" }}
    }, {
      dataField: 'start',
      text: 'Creation date',
      sort: true,
      formatter: (cell, row) => {return this.humanDate(cell)},
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
      headerStyle: () => {return { width: "10%" }},
      sort: true
    }, {
      dataField: 'error_message',
      text: 'Message'
    }, {
      // buttons
      text: 'Actions',
      formatter: (cell, row) => {
        return (
          <div>
            <Button id={row.id} size="sm" outline color="secondary" onClick={this.handlePreview}>Preview</Button>{' '}
            <Button id={row.id} size="sm" outline color="secondary" onClick={this.handleDownload}>Download</Button>{' '}
            <Button id={row.id} size="sm" outline color="secondary" onClick={this.handleRedo}>Redo</Button>
          </div>
        )
      }
    }]

    let defaultSorted = [{
      dataField: 'name',
      order: 'asc'
    }]

    let selectRow = {
      mode: 'checkbox',
      selected: this.props.selected,
      onSelect: this.handleSelection,
      onSelectAll: this.handleSelectionAll
    }

    let noDataIndication = "No datasets"
    if (this.props.waiting) {
      noDataIndication = <WaitingDiv waiting={this.props.waiting} />
    }

    return (
      <div>
        <BootstrapTable
          selectRow={ { mode: 'checkbox' } }
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
