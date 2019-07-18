import React, { Component } from 'react'
import { Router, Route, Switch } from 'react-router-dom'
import createBrowserHistory from 'history/createBrowserHistory'
import axios from 'axios'

import Ask from './routes/ask/ask'
import About from './routes/about/about'
import Jobs from './routes/jobs/jobs'
import Upload from './routes/upload/upload'
import Integration from './routes/integration/integration'
import Datasets from './routes/datasets/datasets'
import Signup from './routes/login/signup'
import Login from './routes/login/login'
import Logout from './routes/login/logout'
import Account from './routes/account/account'
import Admin from './routes/admin/admin'
import Sparql from './routes/sparql/sparql'
import Query from './routes/query/query'
import Results from './routes/results/results'
import AskoNavbar from './navbar'
import AskoFooter from './footer'

import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css'
import 'bootstrap/dist/css/bootstrap.min.css'

const history = createBrowserHistory()

export default class Routes extends Component {
  constructor (props) {
    super(props)
    this.state = {
      waiting: true,
      error: false,
      errorMessage: null,
      logged: false,
      user: {},
      config: {}
    }
    this.cancelRequest
  }

  componentDidMount () {
    let requestUrl = '/api/start'
    axios.get(requestUrl, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          error: false,
          errorMessage: null,
          user: response.data.user,
          logged: response.data.logged,
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

    let admin = false
    if (this.state.user) {
      admin = this.state.user.admin
    }

    let integrationRoutes
    if (!this.state.config.disableIntegration || admin) {
      integrationRoutes = (
        <>
          <Route path="/files" exact component={() => (<Upload waitForStart={this.state.waiting} user={this.state.user} logged={this.state.logged} />)} />
          <Route path="/datasets" exact component={() => (<Datasets waitForStart={this.state.waiting} user={this.state.user} logged={this.state.logged} />)} />
          <Route path="/integration" exact component={Integration} />
        </>
      )
    }


    return (
      <Router history={history}>
        <div>
          <AskoNavbar waitForStart={this.state.waiting} logged={this.state.logged} user={this.state.user} disableIntegration={this.state.config.disableIntegration}/>
          <Switch>
            <Route path="/" exact component={() => (<Ask waitForStart={this.state.waiting} user={this.state.user} logged={this.state.logged} config={this.state.config} />)} />
            <Route path="/about" exact component={() => (<About />)} />
            <Route path="/login" exact component={() => (<Login waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/signup" exact component={() => (<Signup waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/logout" exact component={() => (<Logout waitForStart={this.state.waiting} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/account" exact component={() => (<Account waitForStart={this.state.waiting} user={this.state.user} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/admin" exact component={() => (<Admin waitForStart={this.state.waiting} user={this.state.user} setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/query" exact component={Query} />
            <Route path="/results" exact component={() => (<Results waitForStart={this.state.waiting} user={this.state.user} logged={this.state.logged} />)} />
            <Route path="/sparql" exact component={Sparql} />
            {integrationRoutes}
          </Switch>
          <br />
          <br />
          <AskoFooter version={this.state.config.version} commit={this.state.config.commit} message={this.state.config.footerMessage} />
        </div>
      </Router>
    )
  }
}
