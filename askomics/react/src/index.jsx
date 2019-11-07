import React from 'react'
import ReactDOM from 'react-dom'
import * as Sentry from '@sentry/browser'

import Routes from './routes'

class App extends React.Component {
  render () {

    return (
      <Routes />
    )
  }
}

let sentry = document.getElementById('sentry').getAttribute('sentry')
if (sentry != "") {
  Sentry.init({dsn: sentry});
}

ReactDOM.render(<App/>, document.getElementById('app'))
