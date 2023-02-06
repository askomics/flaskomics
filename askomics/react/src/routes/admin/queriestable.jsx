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

export default class QueriesTable extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.togglePublicQuery = this.togglePublicQuery.bind(this)
    this.handleQuerySelection = this.handleQuerySelection.bind(this)
    this.handleQuerySelectionAll = this.handleQuerySelectionAll.bind(this)
  }

  handleQuerySelection (row, isSelect) {
    if (isSelect) {
      this.props.setStateQueries({
        queriesSelected: [...this.props.queriesSelected, row.id]
      })
    } else {
      this.props.setStateQueries({
        queriesSelected: this.props.queriesSelected.filter(x => x !== row.id)
      })
    }
  }

  handleQuerySelectionAll (isSelect, rows) {
    const ids = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStateQueries({
        queriesSelected: ids
      })
    } else {
      this.props.setStateQueries({
        queriesSelected: []
      })
    }
  }

  togglePublicQuery (event) {
    let requestUrl = '/api/admin/publicize_query'
    let data = {
      queryId: parseInt(event.target.id.replace("query-", "")),
      newStatus: event.target.value == 1 ? false : true
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      console.log(requestUrl, response.data)
      this.props.setStateQueries({
        queries: response.data.queries
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.props.setStateQueries({
        queryError: true,
        queryErrorMessage: error.response.data.errorMessage,
        queryStatus: error.response.status,
      })
    })
  }

  render () {
    let queriesColumns = [{
      dataField: 'user',
      text: 'User',
      sort: true
    }, {
      dataField: 'description',
      text: 'Description',
      sort: true,
      editable: false
    }, {
      dataField: 'start',
      text: 'Creation date',
      sort: true,
      formatter: (cell, row) => { return this.utils.humanDate(cell) },
      editable: false
    },  {
      dataField: 'execTime',
      text: 'Exec time',
      sort: true,
      formatter: (cell, row) => { return row.status != "started" ? cell == 0 ? '<1s' : pretty([cell, 0], 's') : ""},
      editable: false
    }, {
      dataField: "nrows",
      text: "Rows",
      sort: true,
      formatter: (cell, row) => {
        if (row.status != "success") {
          return ""
        } else {
          let formattedNrows = new Intl.NumberFormat('fr-FR').format(cell)
          return formattedNrows
        }
      },
      editable: false
    }, {
      dataField: "size",
      text: "Size",
      sort: true,
      formatter: (cell, row) => {
        return cell ? this.utils.humanFileSize(cell, true) : ''
      },
      editable: false
    },{
      dataField: 'public',
      text: 'Public',
      sort: true,
      formatter: (cell, row) => {
        return (
          <FormGroup>
            <div>
              <CustomInput disabled={!cell} type="switch" id={"query-" + row.id} onChange={this.togglePublicQuery} checked={cell} value={cell} />
            </div>
          </FormGroup>
        )
      },
      editable: false
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
          return <Badge color="warning">Deleting...</Badge>
        }
        return <Badge style={{cursor: "pointer"}} id={row.id} color="danger" >Failure</Badge>
      },
      sort: true,
      editable: false
    }]

    let queriesDefaultSorted = [{
      dataField: 'start',
      order: 'desc'
    }]

    let queriesNoDataIndication = 'No queries'
    if (this.props.queriesLoading) {
      queriesNoDataIndication = <WaitingDiv waiting={this.props.queriesLoading} />
    }

    let queriesSelectRow = {
      mode: 'checkbox',
      clickToSelect: false,
      selected: this.props.queriesSelected,
      onSelect: this.handleQuerySelection,
      onSelectAll: this.handleQuerySelectionAll,
    }

    return (
      <div className="asko-table-height-div">
        <BootstrapTable
          classes="asko-table"
          wrapperClasses="asko-table-wrapper"
          tabIndexCell
          bootstrap4
          keyField='id'
          data={this.props.queries}
          columns={queriesColumns}
          defaultSorted={queriesDefaultSorted}
          pagination={paginationFactory()}
          noDataIndication={queriesNoDataIndication}
          selectRow={ queriesSelectRow }
        />
      </div>
    )
  }
}

QueriesTable.propTypes = {
    setStateQueries: PropTypes.func,
    queriesSelected: PropTypes.object,
    queriesLoading: PropTypes.bool,
    queries: PropTypes.object,
    config: PropTypes.object
}
