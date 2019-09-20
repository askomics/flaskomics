import React, { Component } from 'react'
import { Redirect } from 'react-router'
import axios from 'axios'
import update from 'immutability-helper'
import PropTypes from 'prop-types'


export default class logout extends Component {
  constructor (props) {
    super(props)
    this.cancelRequest
  }

  componentDidMount () {
    let requestUrl = '/api/auth/logout'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath })
      .then(response => {
        console.log(requestUrl, response.data)
        this.props.setStateNavbar({
          config: update(this.props.config, {
            user: {$set: response.data.user},
            logged: {$set: response.data.logged}
          })
        })
      })
      .catch(error => {
        console.log(error)
      })
  }

  render () {
    return <Redirect to="/" />
  }
}

logout.propTypes = {
  setStateNavbar: PropTypes.func,
  config: PropTypes.object
}
