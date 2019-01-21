import React from 'react'
import ReactDOM from 'react-dom'
import axios from 'axios'

import Routes from './routes'

class App extends React.Component {
  render() {
    return (
      <div>
        <Routes />
      </div>
    )
  }
}

ReactDOM.render(<App />, document.getElementById('app'))
