import React, { Component } from 'react'
import axios from 'axios'
import { Button, Form, FormGroup, Label, Input, Alert, Col } from 'reactstrap'
import { Redirect } from 'react-router'
import { Link } from 'react-router-dom'
import UpdateProfile from './update_profile'
import UpdatePassword from './update_password'
import UpdateGalaxyAccount from './update_galaxy'
import DeleteAccount from './delete_account'
import UpdateApiKey from './update_apikey'
import PropTypes from 'prop-types'
import WaitingDiv from '../../components/waiting'

export default class Account extends Component {
  constructor (props) {
    super(props)
    this.state = { isLoading: true,
      error: false,
      errorMessage: []
    }
  }

  render () {
    if (!this.props.waitForStart && !this.props.config.logged) {
      return <Redirect to="/login" />
    }

    if (this.props.waitForStart) {
      return <WaitingDiv waiting={this.props.waitForStart} center />
    }

    let updateProfile
    if (this.props.config.user.ldap == 0) {
      updateProfile = (
        <div>
          <hr />
          <UpdateProfile config={this.props.config} setStateNavbar={this.props.setStateNavbar} />
        </div>
      )
    }

    let updatePassword
    if (this.props.config.user.ldap == 0) {
      updatePassword = (
        <div>
          <hr />
          <UpdatePassword config={this.props.config} setStateNavbar={this.props.setStateNavbar} />
        </div>
      )
    }


    return (
      <div className="container">
        <h2>{this.props.config.user.fname} {this.props.config.user.lname}</h2>
        {updateProfile}
        {updatePassword}
        <hr />
        <UpdateGalaxyAccount config={this.props.config} setStateNavbar={this.props.setStateNavbar} />
        <hr />
        <UpdateApiKey config={this.props.config} setStateNavbar={this.props.setStateNavbar} />
        <hr />
        <DeleteAccount config={this.props.config} setStateNavbar={this.props.setStateNavbar} />
      </div>
    )
  }
}

Account.propTypes = {
  config: PropTypes.object,
  setStateNavbar: PropTypes.func,
  waitForStart: PropTypes.bool
}
