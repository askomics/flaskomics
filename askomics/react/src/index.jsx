import React from 'react'
import ReactDOM from 'react-dom'
import axios from 'axios'
import { BrowserRouter as Router } from "react-router-dom";

import Routes from './routes'
import Navbar from './navbar'

class App extends React.Component {
  render() {
    return (
      <Router>
        <div>
          <Navbar />
          <Routes />
        </div>
      </Router>
    )
  }
}

ReactDOM.render(<App />, document.getElementById('app'))
