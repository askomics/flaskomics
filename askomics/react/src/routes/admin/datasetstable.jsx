import React, { Component } from 'react'
import axios from 'axios'
import {Badge, Button, Form, FormGroup, Label, Input, Alert, Row, Col, CustomInput } from 'reactstrap'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import cellEditFactory from 'react-bootstrap-table2-editor'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'
import WaitingDiv from '../../components/waiting'
import pretty from 'pretty-time'

export default class DatasetsTable extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.togglePublicDataset = this.togglePublicDataset.bind(this)
    this.handleDatasetSelection = this.handleDatasetSelection.bind(this)
    this.handleDatasetSelectionAll = this.handleDatasetSelectionAll.bind(this)
  }

  handleDatasetSelection (row, isSelect) {
    if (isSelect) {
      this.props.setStateDatasets({
        datasetsSelected: [...this.props.datasetsSelected, row.id]
      })
    } else {
      this.props.setStateDatasets({
        datasetsSelected: this.props.datasetsSelected.filter(x => x !== row.id)
      })
    }
  }

  handleDatasetSelectionAll (isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStateDatasets({
        datasetsSelected: ids
      })
    } else {
      this.props.setStateDatasets({
        datasetsSelected: []
      })
    }
  }

  togglePublicDataset (event) {
    let requestUrl = '/api/admin/publicize_dataset'
    let data = {
      datasetId: event.target.id,
      newStatus: event.target.value == "true" ? false : true
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      console.log(requestUrl, response.data)
      this.props.setStateDatasets({
        datasets: response.data.datasets
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.props.setStateDatasets({
        datasetError: true,
        datasetErrorMessage: error.response.data.errorMessage,
        datasetStatus: error.response.status,
      })
    })
  }



render () {

    let datasetsColumns = [{
      dataField: 'user',
      text: 'User',
      sort: true
    },{
      dataField: 'name',
      text: 'Dataset name',
      sort: true
    }, {
      dataField: 'start',
      text: 'Creation date',
      sort: true,
      formatter: (cell, row) => { return this.utils.humanDate(cell) }
    }, {
      dataField: 'exec_time',
      text: 'Exec time',
      sort: true,
      formatter: (cell, row) => { return ["started", "queued"].indexOf(row.status) == -1 ? cell == 0 ? '<1s' : pretty([cell, 0], 's') : ""},
      editable: false
    }, {

      dataField: 'public',
      text: 'Public',
      sort: true,
      formatter: (cell, row) => {
        return (
          <FormGroup>
            <div>
              <CustomInput type="switch" id={row.id} onChange={this.togglePublicDataset} checked={cell} value={cell} />
            </div>
          </FormGroup>
        )
      }
    }, {
      dataField: 'ntriples',
      text: 'Triples',
      sort: true,
      formatter: (cell, row) => {
        return cell == 0 ? '' : new Intl.NumberFormat('fr-FR').format(cell)
      }
    }, {
      dataField: 'status',
      text: 'Status',
      formatter: (cell, row) => {
        if (cell == 'queued') {
          return <Badge color="secondary">Queued</Badge>
        }
        if (cell == 'started') {
          return <Badge color="info">{row.percent ? "processing (" + Math.round(row.percent) + "%)" : "started"}</Badge>
        }
        if (cell == 'success') {
          return <Badge color="success">Success</Badge>
        }
        if (cell == 'deleting') {
          return <Badge color="warning">Deleting</Badge>
        }
        return <Badge style={{cursor: "pointer"}} id={row.id} color="danger">Failure</Badge>
      },
      sort: true
    }]

    let datasetsDefaultSorted = [{
      dataField: 'start',
      order: 'desc'
    }]

    let datasetsSelectRow = {
      mode: 'checkbox',
      selected: this.props.selected,
      onSelect: this.handleDatasetSelection,
      onSelectAll: this.handleDatasetSelectionAll
    }

    let datasetsNoDataIndication = 'No datasets'
    if (this.props.datasetsLoading) {
      datasetsNoDataIndication = <WaitingDiv waiting={this.props.datasetsLoading} />
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
          columns={datasetsColumns}
          defaultSorted={datasetsDefaultSorted}
          pagination={paginationFactory()}
          noDataIndication={datasetsNoDataIndication}
          selectRow={ datasetsSelectRow }
        />
      </div>
    )
  }
}

DatasetsTable.propTypes = {
  setStateDatasets: PropTypes.func,
  datasetsSelected: PropTypes.object,
  datasetsLoading: PropTypes.bool,
  datasets: PropTypes.object,
  config: PropTypes.object
}
