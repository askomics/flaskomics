import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import WaitingDiv from '../../components/waiting'
import { Badge, FormGroup, CustomInput, Modal, ModalHeader, ModalBody, ModalFooter, Button } from 'reactstrap'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'
import SyntaxHighlighter from 'react-syntax-highlighter'
import { monokai } from 'react-syntax-highlighter/dist/esm/styles/hljs'

export default class DatasetsTable extends Component {
  constructor (props) {
    super(props)
    this.state = {
      modalTracebackTitle: "",
      modalTracebackContent: "",
      modalTraceback: false
    }
    this.utils = new Utils()
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
    this.togglePublicDataset = this.togglePublicDataset.bind(this)
    this.handleClickError = this.handleClickError.bind(this)
    this.toggleModalTraceback = this.toggleModalTraceback.bind(this)
  }

  handleSelection (row, isSelect) {
    if (isSelect) {
      this.props.setStateDatasets({
        selected: [...this.props.selected, row.id]
      })
    } else {
      this.props.setStateDatasets({
        selected: this.props.selected.filter(x => x !== row.id)
      })
    }
  }

  handleSelectionAll (isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStateDatasets({
        selected: ids
      })
    } else {
      this.props.setStateDatasets({
        selected: []
      })
    }
  }

  handleClickError(event) {
    this.props.datasets.forEach(dataset => {
      if (dataset.id == event.target.id) {
        this.setState({
          modalTracebackTitle: dataset.error_message ? dataset.error_message : "Internal server error",
          modalTracebackContent: dataset.traceback ? dataset.traceback : "Internal server error",
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

  togglePublicDataset (event) {
    let requestUrl = '/api/datasets/public'
    let data = {
      id: event.target.id,
      newStatus: event.target.value == "true" ? false : true
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      console.log(requestUrl, response.data)
      this.props.setStateDatasets({
        datasets: response.data.datasets
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.props.setStateDatasets({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          waiting: false
        })
      })
    })
  }

  render () {
    let columns = [{
      dataField: 'name',
      text: 'Dataset name',
      sort: true
    }, {
      dataField: 'start',
      text: 'Creation date',
      sort: true,
      formatter: (cell, row) => { return this.utils.humanDate(cell) }
    }, {

      dataField: 'public',
      text: 'Public',
      sort: true,
      formatter: (cell, row) => {
        return (
          <FormGroup>
            <div>
              <CustomInput disabled={this.props.config.user.admin ? false : true} type="switch" id={row.id} onChange={this.togglePublicDataset} checked={cell} value={cell} />
            </div>
          </FormGroup>
        )
      }
    }, {
      dataField: 'ntriples',
      text: 'Triples',
      sort: true,
      formatter: (cell, row) => {
        return new Intl.NumberFormat('fr-FR').format(cell)
      }
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
          return <Badge color="warning">Deleting</Badge>
        }
        return <Badge style={{cursor: "pointer"}} id={row.id} color="danger" onClick={this.handleClickError}>Failure</Badge>
      },
      sort: true
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

    let noDataIndication = 'No datasets'
    if (this.props.waiting) {
      noDataIndication = <WaitingDiv waiting={this.props.waiting} />
    }

    return (
      <div>
        <div className="asko-table-height-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            tabIndexCell
            bootstrap4
            keyField='id'
            data={this.props.datasets}
            columns={columns}
            defaultSorted={defaultSorted}
            pagination={paginationFactory()}
            noDataIndication={noDataIndication}
            selectRow={ selectRow }
          />
        </div>
        <Modal size="lg" isOpen={this.state.modalTraceback} toggle={this.toggleModalTraceback}>
          <ModalHeader toggle={this.toggleModalTraceback}>{this.state.modalTracebackTitle}</ModalHeader>
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
      </div>
    )
  }
}

DatasetsTable.propTypes = {
  setStateDatasets: PropTypes.func,
  selected: PropTypes.object,
  waiting: PropTypes.bool,
  datasets: PropTypes.object,
  config: PropTypes.object
}