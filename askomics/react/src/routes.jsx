import React, { Component } from "react"
import { Router, Route, Switch } from "react-router"
import createBrowserHistory from 'history/createBrowserHistory'
import axios from 'axios'

import Home from './home'
import Ask from './ask'
import Jobs from './jobs'
import Upload from './upload'
import Datasets from './datasets'
import Signup from './signup'
import Login from './login'
import Logout from './logout'
import AskoNavbar from './navbar'
import AskoFooter from './footer'

const history = createBrowserHistory()

export default class Routes extends Component {

  constructor(props) {
    super(props)
    this.state = {
      error: false,
      errorMessage: null,
      logged: false,
      user: {}
    }
  }

  componentDidMount() {

    let requestUrl = '/api/start'
    axios.get(requestUrl)
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        error: false,
        errorMessage: null,
        user: response.data.user,
        logged: response.data.logged,
        version: response.data.version,
        footerMessage: response.data.footer_message
      })
    })
    .catch( (error) => {
      console.log(error)
    })
  }

  render() {
    return (
      <Router history={history}>
        <div>
          <AskoNavbar logged={this.state.logged} user={this.state.user}/>
          <Switch>
            <Route path="/" exact component={() => (<Ask user={this.state.user} logged={this.state.logged} />)} />
            <Route path="/login" exact component={() => (<Login setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/signup" exact component={() => (<Signup setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/logout" exact component={() => (<Logout setStateNavbar={p => this.setState(p)} />)} />
          </Switch>
          <br />
          <AskoFooter version={this.state.version} message={this.state.footerMessage} />
        </div>
      </Router>
    )
  }
}
