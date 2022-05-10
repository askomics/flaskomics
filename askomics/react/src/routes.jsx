import React, { Component, createContext } from 'react'
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom'
import axios from 'axios'

import Ask from './routes/ask/ask'
import About from './routes/about/about'
import Upload from './routes/upload/upload'
import Integration from './routes/integration/integration'
import Data from './routes/data/data'
import Datasets from './routes/datasets/datasets'
import Signup from './routes/login/signup'
import Login from './routes/login/login'
import Logout from './routes/login/logout'
import PasswordReset from './routes/login/passwordreset'
import Account from './routes/account/account'
import Admin from './routes/admin/admin'
import Sparql from './routes/sparql/sparql'
import FormQuery from './routes/form/query'
import FormEditQuery from './routes/form_edit/query'
import Query from './routes/query/query'
import Results from './routes/results/results'
import AskoNavbar from './navbar'
import AskoFooter from './footer'

import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'react-datepicker/dist/react-datepicker.css'

export default class Routes extends Component {

  constructor (props) {
    super(props)
    this.state = {
      waiting: true,
      error: false,
      errorMessage: null,
      config: {
        proxyPath: document.getElementById('proxy_path').getAttribute('proxy_path'),
        user: {},
        logged: false,
        footerMessage: null,
        version: null,
        commit: null,
        gitUrl: null,
        disableIntegration: null,
        namespaceData: null,
        namespaceInternal: null,
        singleTenant: false
      }
    }
    this.cancelRequest
  }

  componentDidMount () {

    let requestUrl = '/api/start'
    axios.get(requestUrl, {baseURL: this.state.config.proxyPath , cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          error: false,
          errorMessage: null,
          config: response.data.config,
          waiting: false
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          waiting: false
        })
      })
  }

  render () {

    let redirectRoot

    if (document.getElementById('redirect').getAttribute('redirect') == "/") {
      redirectRoot = <Redirect to="/" />
    }

    let admin = false
    if (this.state.config.user) {
      admin = this.state.config.user.admin
    }

    let integrationRoutes
    if (!this.state.config.disableIntegration || admin) {
      integrationRoutes = (
        <>
          <Route path="/files" exact component={() => (<Upload config={this.state.config} waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
          <Route path="/datasets" exact component={() => (<Datasets config={this.state.config} waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
          <Route path="/integration" exact component={Integration} />
        </>
      )
    }


    return (
      <Router basename={this.state.config.proxyPath}>
        <div>
          {redirectRoot}
          <AskoNavbar waitForStart={this.state.waiting} config={this.state.config} />
          <Switch>
            <Route path="/" exact component={() => (<Ask waitForStart={this.state.waiting} config={this.state.config} />)} />
            <Route path="/about" exact component={() => (<About />)} />
            <Route path="/login" exact component={() => (<Login config={this.state.config} waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/signup" exact component={() => (<Signup config={this.state.config} waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/logout" exact component={() => (<Logout config={this.state.config} waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/password_reset" component={(props) => <PasswordReset config={this.state.config} waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} {...props}/>}/>
            <Route path="/account" exact component={() => (<Account config={this.state.config} waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/admin" exact component={() => (<Admin config={this.state.config} waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/query" exact component={Query} />
            <Route path="/form" exact component={FormQuery} />
            <Route path="/form_edit" exact component={FormEditQuery} />
            <Route path="/results" exact component={() => (<Results config={this.state.config} waitForStart={this.state.waiting} />)} />
            <Route path="/sparql" render={(props) => <Sparql config={this.state.config} waitForStart={this.state.waiting} {...props}/>}/>
            <Route path="/data/:uri" exact component={() => (<Data config={this.state.config} waitForStart={this.state.waiting} />)} />
            {integrationRoutes}
          </Switch>
          <br />
          <br />
          <AskoFooter config={this.state.config} />
        </div>
      </Router>
    )
  }
}
