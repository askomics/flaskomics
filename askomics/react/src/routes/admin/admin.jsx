import React, { Component } from 'react'
import axios from 'axios'
import { Button, Form, FormGroup, Label, Input, Alert, Row, Col, CustomInput } from 'reactstrap'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import cellEditFactory from 'react-bootstrap-table2-editor'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'
import { Redirect } from 'react-router-dom'
import WaitingDiv from '../../components/waiting'
import ErrorDiv from '../error/error'

export default class Admin extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = { isLoading: true,
      error: false,
      errorMessage: '',
      users: [],
      fname: "",
      lname: "",
      username: "",
      email: "",
      newUser: {},
      messageOpen: false,
      displayPassword: false,
      instanceUrl: "",
      selected: []
    }
    this.handleChangeAdmin = this.handleChangeAdmin.bind(this)
    this.handleChangeBlocked = this.handleChangeBlocked.bind(this)
    this.handleChangeUserInput = this.handleChangeUserInput.bind(this)
    this.handleChangeFname = this.handleChangeFname.bind(this)
    this.handleChangeLname = this.handleChangeLname.bind(this)
    this.handleAddUser = this.handleAddUser.bind(this)
    this.dismissMessage = this.dismissMessage.bind(this)
    this.handleSelection = this.handleSelection.bind(this)
    this.handleSelectionAll = this.handleSelectionAll.bind(this)
    this.deleteSelectedUsers = this.deleteSelectedUsers.bind(this)
    this.cancelRequest
  }

  handleSelection (row, isSelect) {
    if (isSelect) {
      this.setState({
        selected: [...this.state.selected, row.username]
      })
    } else {
      this.setState({
        selected: this.state.selected.filter(x => x !== row.username)
      })
    }
  }

  handleSelectionAll (isSelect, rows) {
    const usernames = rows.map(r => r.username)
    if (isSelect) {
      this.setState({
        selected: usernames
      })
    } else {
      this.setState({
        selected: []
      })
    }
  }

  isDisabled () {
    return this.state.selected.length == 0
  }

  deleteSelectedUsers () {
    let requestUrl = '/api/admin/delete_users'
    let data = {
      usersToDelete: this.state.selected
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          users: response.data.users,
          selected: [],
          waiting: false
        })
      })
  }

  dismissMessage () {
    this.setState({
      newUser: {},
      messageOpen: false
    })
  }

  handleChangeFname (event) {
    this.setState({
      username: event.target.value.charAt(0).toLowerCase(),
      fname: event.target.value
    })
  }

  handleChangeLname (event) {
    this.setState({
      username: this.state.fname.charAt(0).toLowerCase() + event.target.value.toLowerCase(),
      lname: event.target.value
    })
  }

  handleChangeUserInput (event) {
    this.setState({
      [event.target.id]: event.target.value
    })
  }

  validateEmail (email) {
    let re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    return re.test(String(email).toLowerCase())
  }

  validateForm () {
    return (
      this.state.fname.length > 0 &&
      this.state.lname.length > 0 &&
      this.validateEmail(this.state.email) &&
      this.state.username.length > 0
    )
  }

  handleAddUser(event) {

    let requestUrl = "/api/admin/adduser"
    let data = {
      fname: this.state.fname,
      lname: this.state.lname,
      username: this.state.username,
      email: this.state.email
    }

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        error: response.data.error,
        errorMessage: response.data.errorMessage,
        status: response.status,
        newUser: response.data.user,
        messageOpen: true,
        displayPassword: response.data.displayPassword,
        instanceUrl: response.data.instanceUrl
      })
      if (!response.data.error) {
        this.loadUsers()
      }
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
    event.preventDefault()
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

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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

    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
          success: !error.response.data.error
        })
      })
  }

  componentDidMount () {
    if (!this.props.waitForStart) {
      this.loadUsers()
    }
  }

  loadUsers() {
    let requestUrl = '/api/admin/getusers'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          fname: "",
          lname: "",
          username: "",
          email: "",
          isLoading: false,
          users: response.data.users
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
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
    let index = this.state.users.findIndex((user) => user.username == username)

    console.log("index", index)

    let requestUrl = '/api/admin/setquota'
    let data = {
      username: username,
      quota: newValue
    }
    axios.post(requestUrl, data, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
          this.setState({
            error: true,
            errorMessage: error.response.data.errorMessage,
            status: error.response.status,
            success: !error.response.data.error
          })
    })
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  render () {
    let columns = [{
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
    }]

    let defaultSorted = [{
      dataField: 'fname',
      order: 'asc'
    }]

    if (!this.props.waitForStart && !this.props.config.logged) {
      return <Redirect to="/login" />
    }
    if (!this.props.waitForStart && this.props.config.user.admin != 1) {
      return <Redirect to="/" />
    }

    if (this.props.waitForStart) {
      return <WaitingDiv waiting={this.props.waitForStart} center />
    }

    let newUserMessage
    if (this.state.displayPassword) {
      newUserMessage = (
        <Alert color="info" isOpen={this.state.messageOpen} toggle={this.dismissMessage}>
          Send the following message to the new user as AskOmics is not configured to send emails. Once the message is closed, there is no way to recover the password.
          <hr />
          Welcome {this.state.newUser.username}! An AskOmics account has been created for on <a href={this.state.instanceUrl}>{this.state.instanceUrl}</a>.<br /><br />

          Username: <b>{this.state.newUser.username}</b><br />
          Email: <b>{this.state.newUser.email}</b><br />
          Password: <b>{this.state.newUser.password}</b><br /><br />

          Please change the password as soon as possible.<br /><br />

          Thanks,<br />
          The AskOmics Team
        </Alert>
      )
    } else {
      newUserMessage = (
        <Alert color="info" isOpen={this.state.messageOpen} toggle={this.dismissMessage}>
          User {this.state.newUser.username} added. Password creation link send to {this.state.newUser.email}
        </Alert>
      )
    }

    let selectRow = {
      mode: 'checkbox',
      clickToSelect: true,
      selected: this.state.selected,
      onSelect: this.handleSelection,
      onSelectAll: this.handleSelectionAll,
      nonSelectable: [this.props.config.user.username]
    }

    return (
      <div className="container">
        <h2>Admin</h2>
        <hr />
        <h4>Add a user</h4>
        <div>
        <Form onSubmit={this.handleAddUser}>
          <Row form>
            <Col md={3}>
              <FormGroup>
                <Label for="fname">First name</Label>
                <Input type="text" name="fname" id="fname" placeholder="first name" value={this.state.fname} onChange={this.handleChangeFname} />
              </FormGroup>
            </Col>
            <Col md={3}>
              <FormGroup>
                <Label for="lname">Last name</Label>
                <Input type="text" name="lname" id="lname" placeholder="last name" value={this.state.lname} onChange={this.handleChangeLname} />
              </FormGroup>
            </Col>
            <Col md={3}>
              <FormGroup>
                <Label for="username">Username</Label>
                <Input type="text" name="username" id="username" placeholder="username" value={this.state.username} onChange={this.handleChangeUserInput} />
              </FormGroup>
            </Col>
            <Col md={3}>
              <FormGroup>
                <Label for="email">Email</Label>
                <Input type="email" name="email" id="email" placeholder="email" value={this.state.email} onChange={this.handleChangeUserInput} />
              </FormGroup>
            </Col>
          </Row>
          <Button disabled={!this.validateForm()}>Create</Button>
        </Form>
        <br />
        </div>

        {newUserMessage}

        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />

        <hr />

        <h4>Users</h4>
        <div className=".asko-table-height-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            bootstrap4
            keyField='username'
            data={this.state.users}
            columns={columns}
            defaultSorted={defaultSorted}
            pagination={paginationFactory()}
            cellEdit={ cellEditFactory({
              mode: 'click',
              autoSelectText: true,
              beforeSaveCell: (oldValue, newValue, row) => { this.updateQuota(oldValue, newValue, row) },
            })}
            selectRow={ selectRow }
          />
          <br />
          <Button disabled={this.isDisabled()} onClick={this.deleteSelectedUsers} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
        </div>
      </div>
    )
  }
}

Admin.propTypes = {
  waitForStart: PropTypes.bool,
  config: PropTypes.object
}