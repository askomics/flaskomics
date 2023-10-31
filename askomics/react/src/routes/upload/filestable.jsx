import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import cellEditFactory from 'react-bootstrap-table2-editor'
import {Badge} from 'reactstrap'
import WaitingDiv from '../../components/waiting'
import Utils from '../../classes/utils'
import PropTypes from 'prop-types'

export default class FilesTable extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
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
        return <Badge color="danger">Error</Badge>
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
