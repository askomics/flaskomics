import React, { Component } from "react"
import axios from 'axios'
import { Button, Form, FormGroup, Label, Input, Alert, Col } from 'reactstrap'
import { Redirect} from 'react-router'
import { Link } from "react-router-dom";
import UpdateProfile from "./update_profile"
import UpdatePassword from "./update_password"

export default class Login extends Component {

  constructor(props) {
    super(props)
    this.state = {isLoading: true,
                  error: false,
                  errorMessage: []
    }
  }

  render() {

    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    let errorDiv
    if (this.state.error) {
      errorDiv = (
        <div>
          <Alert color="danger">
            <i className="fas fa-exclamation-circle"></i> {this.state.errorMessage}
          </Alert>
        </div>
      )
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>{this.props.user.fname} {this.props.user.lname}</h2>
        <hr />
        <UpdateProfile user={this.props.user} setStateNavbar={this.props.setStateNavbar} />
        <hr />
        <UpdatePassword user={this.props.user} setStateNavbar={this.props.setStateNavbar} />
      </div>
    )
  }
}

