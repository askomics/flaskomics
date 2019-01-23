import React, { Component } from "react"
import { Router, Route, Switch } from "react-router"
import createBrowserHistory from 'history/createBrowserHistory'
import axios from 'axios'

import Home from './home'
import Ask from './ask'
import Jobs from './jobs'
import Upload from './upload'
import Datasets from './datasets'
import Login from './login'
import Logout from './logout'
import AskoNavbar from './navbar'

const history = createBrowserHistory()

export default class Routes extends Component {

  constructor(props) {
    super(props)
    this.state = {
      error: false,
      errorMessage: null,
      logged: false,
      username: null
    }
  }

  componentDidMount() {

    let requestUrl = '/api/user'
    axios.get(requestUrl)
    .then(response => {
      console.log('Routes', requestUrl, response.data)
      this.setState({
        error: false,
        errorMessage: null,
        username: response.data.username,
        logged: response.data.logged
      })
    })
    .catch( (error) => {
      console.log(error)
    })
  }

  render() {
    console.log('rendering routes')
    console.log('routes state', this.state)
    return (
      <Router history={history}>
        <div>
          <AskoNavbar logged={this.state.logged} username={this.state.username} />
          <Switch>
            <Route path="/" exact component={() => (<Ask username={this.state.username} logged={this.state.logged} />)} />
            <Route path="/login" exact component={() => (<Login setStateNavbar={p => this.setState(p)} />)} />
            <Route path="/logout" exact component={() => (<Logout setStateNavbar={p => this.setState(p)} />)} />
          </Switch>
        </div>
      </Router>
    )
  }
}
