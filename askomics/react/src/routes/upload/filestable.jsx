import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import cellEditFactory from 'react-bootstrap-table2-editor'
import {Badge, Modal, ModalHeader, ModalBody, ModalFooter, Button} from 'reactstrap'
import WaitingDiv from '../../components/waiting'
import Utils from '../../classes/utils'
import SyntaxHighlighter from 'react-syntax-highlighter'
import { monokai } from 'react-syntax-highlighter/dist/esm/styles/hljs'
import PropTypes from 'prop-types'

export default class FilesTable extends Component {
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
    this.handleClickError = this.handleClickError.bind(this)
    this.toggleModalTraceback = this.toggleModalTraceback.bind(this)
  }

  handleSelection (row, isSelect) {
    if (isSelect) {
      this.props.setStateUpload(() => ({
        selected: [...this.props.selected, row.id]
      }))
    } else {
      this.props.setStateUpload(() => ({
        selected: this.props.selected.filter(x => x !== row.id)
      }))
    }
  }

  handleSelectionAll (isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStateUpload(() => ({
        selected: ids
      }))
    } else {
      this.props.setStateUpload(() => ({
        selected: []
      }))
    }
  }

  handleClickError(event) {
    this.props.files.forEach(file => {
      if (file.id == event.target.id) {
        this.setState({
          modalTracebackTitle: "File processing error",
          modalTracebackContent: file.preview_error ? file.preview_error : "Internal server error",
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

  editFileName (oldValue, newValue, row) {

    if (newValue === oldValue) {return}

    let requestUrl = '/api/files/editname'
    let data = {
      id: row.id,
      newName: newValue
    }
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      this.props.setStateUpload({
        files: response.data.files,
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

  render () {
    let columns = [{
      dataField: 'name',
      text: 'File name',
      sort: true
    }, {
      dataField: 'date',
      text: 'Date',
      sort: true,
      formatter: (cell, row) => { return this.utils.humanDate(cell) },
      editable: false
    }, {
      dataField: 'type',
      text: 'Type',
      sort: true,
      editable: false
    }, {
      dataField: 'size',
      text: 'File size',
      formatter: (cell, row) => { return this.utils.humanFileSize(cell, true) },
      sort: true,
      editable: false
    }, {
      dataField: 'status',
      text: 'File status',
      formatter: (cell, row) => {
        if (cell == 'downloading') {
          return <Badge color="secondary">Downloading</Badge>
        }
        if (cell == 'available') {
          return <Badge color="success">Available</Badge>
        }
        if (cell == 'processing') {
          return <Badge color="secondary">Processing</Badge>
        }
        return <Badge style={{cursor: "pointer"}} id={row.id} color="danger" onClick={this.handleClickError}>Error</Badge>
      },
      sort: true,
      editable: false
    }]

    let defaultSorted = [{
      dataField: 'date',
      order: 'desc'
    }]

    let selectRow = {
      mode: 'checkbox',
      selected: this.props.selected,
      onSelect: this.handleSelection,
      onSelectAll: this.handleSelectionAll
    }

    let noDataIndication = 'No file uploaded'
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
              data={this.props.files}
              columns={columns}
              defaultSorted={defaultSorted}
              pagination={paginationFactory()}
              noDataIndication={noDataIndication}
              selectRow={ selectRow }
              cellEdit={ cellEditFactory({
                mode: 'click',
                autoSelectText: true,
                beforeSaveCell: (oldValue, newValue, row) => { this.editFileName(oldValue, newValue, row) },
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
      </div>
    )
  }
}

FilesTable.propTypes = {
  selected: PropTypes.bool,
  files: PropTypes.object,
  config: PropTypes.object,
  waiting: PropTypes.bool,
  setStateUpload: PropTypes.func,
}
