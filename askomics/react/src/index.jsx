import React from 'react'
import ReactDOM from 'react-dom'
import * as Sentry from '@sentry/browser'
import packageJson from '../../../package.json';

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
  Sentry.init({
    dsn: sentry,
    release: packageJson.name + "@" + packageJson.version
  });
}

ReactDOM.render(<App/>, document.getElementById('app'))
