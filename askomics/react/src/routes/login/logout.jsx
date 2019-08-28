import React, { Component } from 'react'
import { Redirect } from 'react-router'
import axios from 'axios'
import PropTypes from 'prop-types'
import AskoContext from '../../components/context'


export default class logout extends Component {
  static contextType = AskoContext
  constructor (props) {
    super(props)
    this.cancelRequest
  }

  componentDidMount () {
    let requestUrl = '/api/auth/logout'
    axios.get(requestUrl, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.props.setStateNavbar({
          username: response.data.username,
          logged: response.data.logged
        })
      })
      .catch(error => {
        console.log(error)
      })
  }

  componentWillUnmount () {
    this.cancelRequest()
  }

  render () {
    return <Redirect to="/" />
  }
}

logout.propTypes = {
  setStateNavbar: PropTypes.func
}