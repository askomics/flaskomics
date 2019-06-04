import React, { Component } from 'react'
import axios from 'axios'
import { Button, Form, FormGroup, Label, Input, Alert, Col, CustomInput } from 'reactstrap'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import update from 'react-addons-update'
import PropTypes from 'prop-types'

export default class Admin extends Component {
  constructor (props) {
    super(props)
    this.state = { isLoading: true,
      error: false,
      errorMessage: '',
      users: []
    }
    this.handleChangeAdmin = this.handleChangeAdmin.bind(this)
    this.handleChangeBlocked = this.handleChangeBlocked.bind(this)
    this.cancelRequest
  }

  handleChangeAdmin (event) {
    let username = event.target.getAttribute('username')
    let index = this.state.users.findIndex((user) => user.username == username)

    let newAdmin = 0
    if (event.target.value == 0) {
      newAdmin = 1
    }

    let requestUrl = '/api/admin/setadmin'
    let data = {
      username: username,
      newAdmin: newAdmin
    }

    axios.post(requestUrl, data, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          error: response.data.error,
          errorMessage: response.data.errorMessage,
          success: !response.data.error,
          users: update(this.state.users, { [index]: { admin: { $set: newAdmin } } })
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          success: !response.data.error
        })
      })
  }

  handleChangeBlocked (event) {
    let username = event.target.getAttribute('username')
    let index = this.state.users.findIndex((user) => user.username == username)

    let newBlocked = 0
    if (event.target.value == 0) {
      newBlocked = 1
    }

    let requestUrl = '/api/admin/setblocked'
    let data = {
      username: username,
      newBlocked: newBlocked
    }

    axios.post(requestUrl, data, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          error: response.data.error,
          errorMessage: response.data.errorMessage,
          success: !response.data.error,
          users: update(this.state.users, { [index]: { blocked: { $set: newBlocked } } })
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          success: !response.data.error
        })
      })
  }

  componentDidMount () {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/admin/getusers'

      axios.get(requestUrl, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
          console.log(requestUrl, response.data)
          this.setState({
            isLoading: false,
            error: response.data.error,
            errorMessage: response.data.errorMessage,
            users: response.data.users
          })
        })
        .catch(error => {
          console.log(error, error.response.data.errorMessage)
          this.setState({
            error: true,
            errorMessage: error.response.data.errorMessage,
            status: error.response.status,
            success: !response.data.error
          })
        })
    }
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  render () {
    // console.log()

    let columns = [{
      dataField: 'ldap',
      text: 'Authentication type',
      formatter: (cell, row) => { return cell ? 'Ldap' : 'Local' },
      sort: true
    }, {
      dataField: 'fname',
      text: 'Name',
      formatter: (cell, row) => { return row.fname + ' ' + row.lname },
      sort: true
    }, {
      dataField: 'username',
      text: 'Username',
      sort: true
    }, {
      dataField: 'email',
      text: 'Email',
      formatter: (cell, row) => { return <a href={'mailto:' + cell}>{cell}</a> },
      sort: true
    }, {
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
    }]

    let defaultSorted = [{
      dataField: 'fname',
      order: 'asc'
    }]

    return (
      <div className="container">
        <h2>Admin</h2>
        <hr />
        <BootstrapTable bootstrap4 keyField='id' data={this.state.users} columns={columns} defaultSorted={defaultSorted} pagination={paginationFactory()} />
      </div>
    )
  }
}

Admin.propTypes = {
  waitForStart: PropTypes.bool
}