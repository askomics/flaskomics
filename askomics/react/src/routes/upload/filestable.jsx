import React, { Component } from "react"
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'

export default class FilesTable extends Component {


  constructor(props) {
    super(props)
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
  }

  humanFileSize(bytes, si) {
    let thresh = si ? 1000 : 1024
    if (Math.abs(bytes) < thresh) {
      return bytes + ' B'
    }
    let units = si ? ['kB','MB','GB','TB','PB','EB','ZB','YB'] : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB']
    let u = -1
    do {
      bytes /= thresh
      ++u
    } while(Math.abs(bytes) >= thresh && u < units.length -1)
    return bytes.toFixed(1) + ' ' + units[u]
  }

  handleSelection(row, isSelect) {
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

  handleSelectionAll(isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStateUpload(() => ({
        selected: ids
      }));
    } else {
      this.props.setStateUpload(() => ({
        selected: []
      }))
    }
  }


  render() {

    let columns = [{
      dataField: 'name',
      text: 'File name',
      sort: true
    }, {
      dataField: 'type',
      text: 'Type',
      sort: true
    }, {
      dataField: 'size',
      text: 'File size',
      formatter: (cell, row) => {return this.humanFileSize(cell, true)},
      sort: true
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

    return (
      <div>
        <BootstrapTable
          selectRow={ { mode: 'checkbox' } }
          tabIndexCell
          bootstrap4
          keyField='id'
          data={this.props.files}
          columns={columns}
          defaultSorted={defaultSorted}
          pagination={paginationFactory()}
          noDataIndication="No file uploaded"
          selectRow={ selectRow }
        />
      </div>
    )
  }
}
