import React, { Component } from "react"
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'


export default class FilesTable extends Component {


  constructor(props) {
    super(props)
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

    return (
      <BootstrapTable keyField='id' data={this.props.files} columns={columns} defaultSorted={defaultSorted} pagination={paginationFactory()} />
    )
  }
}
