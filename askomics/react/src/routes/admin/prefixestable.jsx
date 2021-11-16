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

export default class PrefixesTable extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.handlePrefixSelection = this.handlePrefixSelection.bind(this)
    this.handlePrefixSelectionAll = this.handlePrefixSelectionAll.bind(this)
  }

  handlePrefixSelection (row, isSelect) {
    console.log('triggered')
    if (isSelect) {
      this.props.setStatePrefixes({
        prefixesSelected: [...this.props.prefixesSelected, row.id]
      })
    } else {
      this.props.setStatePrefixes({
        prefixesSelected: this.props.prefixesSelected.filter(x => x !== row.id)
      })
    }
  }

  handlePrefixSelectionAll (isSelect, rows) {
    const prefixes = rows.map(r => r.id)
    if (isSelect) {
      this.props.setStatePrefixes({
        prefixesSelected: prefixes
      })
    } else {
      this.props.setStatePrefixes({
        prefixesSelected: []
      })
    }
  }

  render () {
    let prefixesColumns = [{
      editable: false,
      dataField: 'prefix',
      text: 'Prefix',
      sort: true
    }, {
      editable: false,
      dataField: 'namespace',
      text: 'Namespace',
      sort: true
    }]

    let prefixesDefaultSorted = [{
      dataField: 'prefix',
      order: 'asc'
    }]

    let prefixesSelectRow = {
      mode: 'checkbox',
      clickToSelect: false,
      selected: this.props.prefixesSelected,
      onSelect: this.handlePrefixSelection,
      onSelectAll: this.handlePrefixSelectionAll
    }

    let prefixesNoDataIndication = 'No custom prefixes'
    if (this.props.prefixesLoading) {
      prefixesNoDataIndication = <WaitingDiv waiting={this.props.prefixesLoading} />
    }

    return (
        <div className="asko-table-height-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            tabIndexCell
            bootstrap4
            keyField='id'
            data={this.props.prefixes}
            columns={prefixesColumns}
            defaultSorted={prefixesDefaultSorted}
            pagination={paginationFactory()}
            noDataIndication={prefixesNoDataIndication}
            selectRow={ prefixesSelectRow }
          />
        </div>
    )
  }
}

PrefixesTable.propTypes = {
    setStatePrefixes: PropTypes.func,
    prefixesSelected: PropTypes.object,
    prefixesLoading: PropTypes.bool,
    prefixes: PropTypes.array,
    config: PropTypes.object
}
