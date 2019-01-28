import React, { Component } from "react"
import axios from 'axios'
import { Button, Form, FormGroup, Label, Input, Alert, Col } from 'reactstrap'
import { Redirect} from 'react-router'
import { Link } from "react-router-dom";
import UpdateProfile from "./update_profile"
import UpdatePassword from "./update_password"
import UpdateApiKey from "./update_apikey"

export default class Login extends Component {

  constructor(props) {
    super(props)
    this.state = {isLoading: true,
                  error: false,
                  errorMessage: []
    }
  }

  render() {
    return (
      <div className="container">
        <h2>{this.props.user.fname} {this.props.user.lname}</h2>
        <hr />
        <UpdateProfile user={this.props.user} setStateNavbar={this.props.setStateNavbar} />
        <hr />
        <UpdatePassword user={this.props.user} setStateNavbar={this.props.setStateNavbar} />
        <hr />
        <UpdateApiKey user={this.props.user} setStateNavbar={this.props.setStateNavbar} />
      </div>
    )
  }
}

