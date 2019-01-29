import React, { Component } from "react"
import { Redirect } from 'react-router'
import axios from 'axios'

export default class logout extends Component {

  constructor(props) {
    super(props)
  }

  componentDidMount() {
    let requestUrl = '/api/auth/logout'
    axios.get(requestUrl)
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

  render() {
    return <Redirect to="/" />
  }
}

