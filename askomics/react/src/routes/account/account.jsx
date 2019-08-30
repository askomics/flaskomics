import React, { Component } from 'react'
import axios from 'axios'
import { Button, Form, FormGroup, Label, Input, Alert, Col } from 'reactstrap'
import { Redirect } from 'react-router'
import { Link } from 'react-router-dom'
import UpdateProfile from './update_profile'
import UpdatePassword from './update_password'
import UpdateGalaxyAccount from './update_galaxy'
import UpdateApiKey from './update_apikey'
import PropTypes from 'prop-types'

export default class Account extends Component {
  constructor (props) {
    super(props)
    this.state = { isLoading: true,
      error: false,
      errorMessage: []
    }
  }

  render () {
    return (
      <div className="container">
        <h2>{this.props.user.fname} {this.props.user.lname}</h2>
        <hr />
        <UpdateProfile user={this.props.user} setStateNavbar={this.props.setStateNavbar} />
        <hr />
        <UpdatePassword user={this.props.user} setStateNavbar={this.props.setStateNavbar} />
        <hr />
        <UpdateGalaxyAccount user={this.props.user} setStateNavbar={this.props.setStateNavbar} />
        <hr />
        <UpdateApiKey user={this.props.user} setStateNavbar={this.props.setStateNavbar} />
      </div>
    )
  }
}

Account.propTypes = {
  user: PropTypes.object,
  setStateNavbar: PropTypes.func
}
