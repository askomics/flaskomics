import React, { Component } from 'react'
import axios from 'axios'
import {Button, Form, FormGroup, Label, Input, Alert, Row, Col, CustomInput } from 'reactstrap'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import cellEditFactory from 'react-bootstrap-table2-editor'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'
import WaitingDiv from '../../components/waiting'

export default class FilesTable extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.handleFileSelection = this.handleFileSelection.bind(this)
    this.handleFileSelectionAll = this.handleFileSelectionAll.bind(this)
  }

  handleFileSelection (row, isSelect) {
    if (isSelect) {
      this.props.setStateFiles({
        filesSelected: [...this.props.filesSelected, row.id]
      })
    } else {
      this.props.setStateFiles({
        filesSelected: this.props.filesSelected.filter(x => x !== row.id)
      })
    }
  }

  handleFileSelectionAll (isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStateFiles({
        filesSelected: ids
      })
    } else {
      this.props.setStateFiles({
        filesSelected: []
      })
    }
  }

  render () {
    let filesColumns = [{
      dataField: 'user',
      text: 'User',
      sort: true
    },{
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
    }]

    let filesDefaultSorted = [{
      dataField: 'date',
      order: 'desc'
    }]

    let filesSelectRow = {
      mode: 'checkbox',
      selected: this.props.fileSelected,
      onSelect: this.handleFileSelection,
      onSelectAll: this.handleFileSelectionAll
    }

    let filesNoDataIndication = 'No file uploaded'
    if (this.props.filesLoading) {
      filesNoDataIndication = <WaitingDiv waiting={this.props.filesLoading} />
    }

    return (
      <div className="asko-table-height-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            tabIndexCell
            bootstrap4
            keyField='id'
            data={this.props.files}
            columns={filesColumns}
            defaultSorted={filesDefaultSorted}
            pagination={paginationFactory()}
            noDataIndication={filesNoDataIndication}
            selectRow={ filesSelectRow }
          />
      </div>
    )
  }
}

FilesTable.propTypes = {
  setStateFiles: PropTypes.func,
  filesSelected: PropTypes.object,
  filesLoading: PropTypes.bool,
  files: PropTypes.object,
  config: PropTypes.object
}
