import React, { Component } from 'react'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
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

  render () {
    let columns = [{
      dataField: 'name',
      text: 'File name',
      sort: true
    }, {
      dataField: 'date',
      text: 'Date',
      sort: true,
      formatter: (cell, row) => { return this.utils.humanDate(cell) }
    }, {
      dataField: 'type',
      text: 'Type',
      sort: true
    }, {
      dataField: 'size',
      text: 'File size',
      formatter: (cell, row) => { return this.utils.humanFileSize(cell, true) },
      sort: true
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
            />
          </div>
      </div>
    )
  }
}

FilesTable.propTypes = {
  selected: PropTypes.bool,
  files: PropTypes.object,
  waiting: PropTypes.bool,
  setStateUpload: PropTypes.func,
}
