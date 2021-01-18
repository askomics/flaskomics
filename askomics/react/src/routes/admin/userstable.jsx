import React, { Component } from 'react'
import axios from 'axios'
import {Form, FormGroup, Label, Input, Alert, Row, Col, CustomInput } from 'reactstrap'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import cellEditFactory from 'react-bootstrap-table2-editor'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'

export default class UsersTable extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.handleChangeAdmin = this.handleChangeAdmin.bind(this)
    this.handleChangeBlocked = this.handleChangeBlocked.bind(this)
    this.handleUserSelection = this.handleUserSelection.bind(this)
    this.handleUserSelectionAll = this.handleUserSelectionAll.bind(this)
  }

  handleUserSelection (row, isSelect) {
    if (isSelect) {
      this.props.setStateUsers({
        usersSelected: [...this.props.usersSelected, row.username]
      })
    } else {
      this.props.setStateUsers({
        usersSelected: this.props.usersSelected.filter(x => x !== row.username)
      })
    }
  }

  handleUserSelectionAll (isSelect, rows) {
    const usernames = rows.map(r => r.username)
    if (isSelect) {
      this.props.setStateUsers({
        usersSelected: usernames
      })
    } else {
      this.props.setStateUsers({
        usersSelected: []
      })
    }
  }

  handleChangeAdmin (event) {
    let username = event.target.getAttribute('username')
    let index = this.props.users.findIndex((user) => user.username == username)

    let newAdmin = 0
    if (event.target.value == 0) {
      newAdmin = 1
    }

    let requestUrl = '/api/admin/setadmin'
    let data = {
      username: username,
      newAdmin: newAdmin
    }

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.props.setStateUsers({
          userError: response.data.error,
          userErrorMessage: response.data.errorMessage,
          success: !response.data.error,
          users: update(this.props.users, { [index]: { admin: { $set: newAdmin } } })
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.props.setStateUsers({
          userError: true,
          userErrorMessage: error.response.data.errorMessage,
          userStatus: error.response.status,
          success: !response.data.error
        })
      })
  }

  handleChangeBlocked (event) {
    let username = event.target.getAttribute('username')
    let index = this.props.users.findIndex((user) => user.username == username)

    let newBlocked = 0
    if (event.target.value == 0) {
      newBlocked = 1
    }

    let requestUrl = '/api/admin/setblocked'
    let data = {
      username: username,
      newBlocked: newBlocked
    }

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.props.setStateUsers({
          error: response.data.error,
          errorMessage: response.data.errorMessage,
          success: !response.data.error,
          users: update(this.props.users, { [index]: { blocked: { $set: newBlocked } } })
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.props.setStateUsers({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          success: !error.response.data.error
        })
      })
  }

  updateQuota(oldValue, newValue, row) {

    if (newValue === oldValue) {return}

    let username = row.username
    let index = this.props.users.findIndex((user) => user.username == username)

    console.log("index", index)

    let requestUrl = '/api/admin/setquota'
    let data = {
      username: username,
      quota: newValue
    }
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.props.setStateUsers({
          userLoading: false,
          error: response.data.error,
          errorMessage: response.data.errorMessage,
          users: response.data.users
        })
      })
    .catch(error => {
          this.props.setStateUsers({
            error: true,
            errorMessage: error.response.data.errorMessage,
            status: error.response.status,
            success: !error.response.data.error
          })
    })
  }

  render () {
    let usersColumns = [{
      editable: false,
      dataField: 'ldap',
      text: 'Authentication type',
      formatter: (cell, row) => { return cell ? 'Ldap' : 'Local' },
      sort: true
    }, {
      editable: false,
      dataField: 'fname',
      text: 'Name',
      formatter: (cell, row) => { return row.fname + ' ' + row.lname },
      sort: true
    }, {
      editable: false,
      dataField: 'username',
      text: 'Username',
      sort: true
    }, {
      editable: false,
      dataField: 'email',
      text: 'Email',
      formatter: (cell, row) => { return <a href={'mailto:' + cell}>{cell}</a> },
      sort: true
    }, {
      editable: false,
      dataField: 'admin',
      text: 'Admin',
      formatter: (cell, row) => {
        return (
          <FormGroup>
            <div>
              <CustomInput type="switch" username={row.username} id={'set-admin-' + row.username} name="admin" onChange={this.handleChangeAdmin} label="Admin" checked={cell} value={cell} />
            </div>
          </FormGroup>
        )
      },
      sort: true
    }, {
      editable: false,
      dataField: 'blocked',
      text: 'Blocked',
      formatter: (cell, row) => {
        return (
          <FormGroup>
            <div>
              <CustomInput type="switch" username={row.username} id={'set-blocked-' + row.username} name="blocked" onChange={this.handleChangeBlocked} label="Blocked" checked={cell} value={cell} />
            </div>
          </FormGroup>
        )
      },
      sort: true
    }, {
      dataField: 'quota',
      text: 'Quota',
      formatter: (cell, row) => {
        return cell === 0 ? "Unlimited" : this.utils.humanFileSize(cell, true)
      },
      sort: true
    }, {
      dataField: 'last_action',
      text: 'Last action',
      formatter: (cell, row) => { return this.utils.humanDate(cell) },
      editable: false,
      sort: true
    }]

    let usersDefaultSorted = [{
      dataField: 'fname',
      order: 'asc'
    }]

    let usersSelectRow = {
      mode: 'checkbox',
      clickToSelect: false,
      selected: this.state.selected,
      onSelect: this.handleUserSelection,
      onSelectAll: this.handleUserSelectionAll,
      nonSelectable: [this.props.config.user.username]
    }

    return (
      <div className="container">
        <div className=".asko-table-height-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            tabIndexCell
            bootstrap4
            keyField='username'
            data={this.props.users}
            columns={usersColumns}
            defaultSorted={usersDefaultSorted}
            pagination={paginationFactory()}
            cellEdit={ cellEditFactory({
              mode: 'click',
              autoSelectText: true,
              beforeSaveCell: (oldValue, newValue, row) => { this.updateQuota(oldValue, newValue, row) },
            })}
            selectRow={ usersSelectRow }
          />
        </div>
    )
  }
}


UsersTable.propTypes = {
    setStateUsers: PropTypes.func,
    usersSelected: PropTypes.object,
    usersLoading: PropTypes.bool,
    users: PropTypes.object,
    config: PropTypes.object
}
