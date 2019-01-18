// routes.js
import React, { Component } from 'react'
import { Router, Route, Switch } from 'react-router'
import createBrowserHistory from 'history/createBrowserHistory'

import Home from './home'

const history = createBrowserHistory()

export default () =>
  <Router history={history}>
    <Switch>
      <Route path="/" exact component={Home} />
    </Switch>
  </Router>;
