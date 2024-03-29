import React, { Component } from 'react'
import axios from 'axios'
import {Button, Form, FormGroup, Label, Input, Alert, Row, Col, CustomInput } from 'reactstrap'
import PropTypes from 'prop-types'
import DatasetsTable from './datasetstable'
import FilesTable from './filestable'
import QueriesTable from './queriestable'
import UsersTable from './userstable'
import Utils from '../../classes/utils'
import { Redirect } from 'react-router-dom'
import WaitingDiv from '../../components/waiting'
import ErrorDiv from '../error/error'

export default class Admin extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = { usersLoading: true,
      datasetsLoading: true,
      filesLoading: true,
      queriesLoading: true,
      error: false,
      errorMessage: '',
      userError: false,
      userErrorMessage: '',
      fileError: false,
      fileErrorMessage: '',
      datasetError: false,
      datasetErrorMessage: '',
      queryError: false,
      queryErrorMessage: '',
      users: [],
      datasets: [],
      files: [],
      queries: [],
      fname: "",
      lname: "",
      username: "",
      email: "",
      newUser: {},
      messageOpen: false,
      displayPassword: false,
      instanceUrl: "",
      usersSelected: [],
      filesSelected: [],
      datasetsSelected: [],
      queriesSelected: [],
    }
    this.handleChangeUserInput = this.handleChangeUserInput.bind(this)
    this.handleChangeFname = this.handleChangeFname.bind(this)
    this.handleChangeLname = this.handleChangeLname.bind(this)
    this.handleAddUser = this.handleAddUser.bind(this)
    this.dismissMessage = this.dismissMessage.bind(this)
    this.deleteSelectedUsers = this.deleteSelectedUsers.bind(this)
    this.deleteSelectedFiles = this.deleteSelectedFiles.bind(this)
    this.deleteSelectedDatasets = this.deleteSelectedDatasets.bind(this)
    this.deleteSelectedQueries = this.deleteSelectedQueries.bind(this)
    this.cancelRequest
  }

  isUsersDisabled () {
    return this.state.usersSelected.length == 0
  }

  isFilesDisabled () {
    return this.state.filesSelected.length == 0
  }

  isDatasetsDisabled () {
    return this.state.datasetsSelected.length == 0
  }

  isQueriesDisabled () {
    return this.state.queriesSelected.length == 0
  }

  deleteSelectedUsers () {
    let requestUrl = '/api/admin/delete_users'
    let data = {
      usersToDelete: this.state.usersSelected
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          users: response.data.users,
          usersSelected: [],
        })
      })
  }

  deleteSelectedFiles () {
    let requestUrl = '/api/admin/delete_files'
    let data = {
      filesIdToDelete: this.state.filesSelected
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          files: response.data.files,
          filesSelected: [],
        })
      })
  }

  deleteSelectedDatasets () {
    let requestUrl = '/api/admin/delete_datasets'
    let data = {
      datasetsIdToDelete: this.state.datasetsSelected
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          datasets: response.data.datasets,
          datasetsSelected: [],
        })
      })
  }

  deleteSelectedQueries () {
    let requestUrl = '/api/admin/delete_queries'
    let data = {
      queriesIdToDelete: this.state.queriesSelected,
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        this.setState({
          queries: response.data.queries,
          queriesSelected: [],
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

  componentDidMount () {
    if (!this.props.waitForStart) {
      this.loadUsers()
      this.loadDataSets()
      this.loadFiles()
      this.loadQueries()
      this.interval = setInterval(() => {
        this.loadDataSets()
      }, 5000)
    }
  }

  loadDataSets(){
    let requestUrl = '/api/admin/getdatasets'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          datasetsLoading: false,
          datasets: response.data.datasets
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          datasetError: true,
          datasetErrorMessage: error.response.data.errorMessage,
          datasetStatus: error.response.status,
          success: !error.response.data.error
        })
      })
  }

  loadFiles(){
    let requestUrl = '/api/admin/getfiles'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          filesLoading: false,
          files: response.data.files
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          fileError: true,
          fileErrorMessage: error.response.data.errorMessage,
          fileStatus: error.response.status,
          success: !error.response.data.error
        })
      })
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
          usersLoading: false,
          users: response.data.users
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          userError: true,
          userErrorMessage: error.response.data.errorMessage,
          userStatus: error.response.status,
          success: !error.response.data.error
        })
      })
  }

  loadQueries() {
    let requestUrl = '/api/admin/getqueries'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          queriesLoading: false,
          queries: response.data.queries,
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          queryError: true,
          queryErrorMessage: error.response.data.errorMessage,
          queryStatus: error.response.status,
          success: !error.response.data.error
        })
      })
  }

  componentWillUnmount () {
    clearInterval(this.interval)
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  render () {

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
        <UsersTable config={this.props.config} users={this.state.users} setStateUsers={p => this.setState(p)} usersSelected={this.state.usersSelected} usersLoading={this.state.usersLoading} />
        <br />
        <Button disabled={this.isUsersDisabled()} onClick={this.deleteSelectedUsers} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
        <ErrorDiv status={this.state.userStatus} error={this.state.userError} errorMessage={this.state.userErrorMessage} />
        <hr />

        <h4>Files</h4>
        <FilesTable config={this.props.config} files={this.state.files} setStateFiles={p => this.setState(p)} filesSelected={this.state.filesSelected} filesLoading={this.state.filesLoading} />
        <br />
        <Button disabled={this.isFilesDisabled()} onClick={this.deleteSelectedFiles} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
        <ErrorDiv status={this.state.fileStatus} error={this.state.fileError} errorMessage={this.state.fileErrorMessage} />
        <hr />

        <h4>Datasets</h4>
        <DatasetsTable config={this.props.config} datasets={this.state.datasets} setStateDatasets={p => this.setState(p)} datasetsSelected={this.state.datasetsSelected} datasetsLoading={this.state.datasetsLoading} />
        <br />
        <Button disabled={this.isDatasetsDisabled()} onClick={this.deleteSelectedDatasets} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
        <ErrorDiv status={this.state.datasetStatus} error={this.state.datasetError} errorMessage={this.state.datasetErrorMessage} />
        <hr />

        <h4>Queries</h4>
        <QueriesTable config={this.props.config} queries={this.state.queries} setStateQueries={p => this.setState(p)} queriesSelected={this.state.queriesSelected} queriesLoading={this.state.queriesLoading} />
        <br />
        <Button disabled={this.isQueriesDisabled()} onClick={this.deleteSelectedQueries} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
        <ErrorDiv status={this.state.queryStatus} error={this.state.queryError} errorMessage={this.state.queryErrorMessage} />
      </div>
    )
  }
}

Admin.propTypes = {
  waitForStart: PropTypes.bool,
  config: PropTypes.object
}
