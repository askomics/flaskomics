import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import WaitingDiv from '../../components/waiting'
import { Badge, FormGroup, CustomInput } from 'reactstrap'
import PropTypes from 'prop-types'

export default class DatasetsTable extends Component {
  constructor (props) {
    super(props)
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
    this.togglePublicDataset = this.togglePublicDataset.bind(this)
  }

  humanFileSize (bytes, si) {
    let thresh = si ? 1000 : 1024
    if (Math.abs(bytes) < thresh) {
      return bytes + ' B'
    }
    let units = si ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'] : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    let u = -1
    do {
      bytes /= thresh
      ++u
    } while (Math.abs(bytes) >= thresh && u < units.length - 1)
    return bytes.toFixed(1) + ' ' + units[u]
  }

  humanDate (date) {
    let event = new Date(date * 1000)
    return event.toUTCString()
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

  togglePublicDataset (event) {
    let requestUrl = '/api/datasets/public'
    let data = {
      id: event.target.id,
      newStatus: event.target.value == "true" ? false : true
    }
    axios.post(requestUrl, data, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
      formatter: (cell, row) => { return this.humanDate(cell) }
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
      text: 'Triple\'s number',
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
        return <Badge color="danger">Failure</Badge>
      },
      sort: true
    }, {
      dataField: 'error_message',
      text: 'Error message'
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