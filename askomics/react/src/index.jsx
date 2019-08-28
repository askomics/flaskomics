import React from 'react'
import ReactDOM from 'react-dom'
import axios from 'axios'
import { BrowserRouter as Router } from 'react-router-dom'

import Routes from './routes'
import AskoContext from './components/context'

class App extends React.Component {
  render () {

    let value = {
      proxyPath: proxy_path.getAttribute('proxy_path')
    }

    return (
      <AskoContext.Provider value={value}>
        <Routes />
      </AskoContext.Provider>
    )
  }
}

ReactDOM.render(<App proxyPath={ document.getElementById('proxy_path').getAttribute('proxy_path') } />, document.getElementById('app'))
