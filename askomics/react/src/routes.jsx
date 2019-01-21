import React from "react";
import { Route, Switch } from "react-router-dom";

import Home from './home'
import Ask from './ask'
import Jobs from './jobs'
import Upload from './upload'
import Datasets from './datasets'
import Login from './login'

export default () =>
  <Switch>
      <Route path="/" exact component={Home} />
      <Route path="/ask" exact component={Ask} />
      <Route path="/jobs" exact component={Jobs} />
      <Route path="/upload" exact component={Upload} />
      <Route path="/datasets" exact component={Datasets} />
      <Route path="/login" exact component={Login} />
  </Switch>
