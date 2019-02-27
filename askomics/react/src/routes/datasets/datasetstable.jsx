import React, { Component } from "react"
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import WaitingDiv from "../../components/waiting"
import { Badge } from 'reactstrap'

export default class DatasetsTable extends Component {


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

  humanDate(date) {
    let event = new Date(date * 1000)
    return event.toUTCString()
  }

  handleSelection(row, isSelect) {
    if (isSelect) {
      this.props.setStateDatasets(() => ({
        selected: [...this.props.selected, row.id]
      }))
    } else {
      this.props.setStateDatasets(() => ({
        selected: this.props.selected.filter(x => x !== row.id)
      }))
    }
  }

  handleSelectionAll(isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStateDatasets(() => ({
        selected: ids
      }));
    } else {
      this.props.setStateDatasets(() => ({
        selected: []
      }))
    }
  }


  render() {

    let columns = [{
      dataField: 'name',
      text: 'Dataset name',
      sort: true
    }, {
      dataField: 'start',
      text: 'Creation date',
      sort: true,
      formatter: (cell, row) => {return this.humanDate(cell)},
    }, {

      dataField: 'public',
      text: 'Access Level',
      sort: true,
      formatter: (cell, row) => {
        if (cell) {
          return <p className="text-primary"><i className="fas fa-lock"></i> Private</p>
        }else{
          return <p className="text-info"><i className="fas fa-globe-europe"></i> Public</p>
        }
      }
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
      sort: true
    }, {
      dataField: 'error_message',
      text: 'Message'
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
          data={this.props.datasets}
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
