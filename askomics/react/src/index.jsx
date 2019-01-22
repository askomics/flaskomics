import React from 'react'
import ReactDOM from 'react-dom'
import axios from 'axios'
import { BrowserRouter as Router } from "react-router-dom";

import Routes from './routes'
import AskoNavbar from './navbar'

class App extends React.Component {
  render() {
    return (
      <Router>
        <div>
          <AskoNavbar />
          <Routes />
        </div>
      </Router>
    )
  }
}

ReactDOM.render(<App />, document.getElementById('app'))
