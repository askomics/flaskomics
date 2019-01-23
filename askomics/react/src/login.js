import React, { Component } from "react"
import axios from 'axios'
import { Button, Form, FormGroup, Label, Input } from 'reactstrap'
import { Redirect} from 'react-router'

export default class Login extends Component {

  constructor(props) {
    super(props)
    this.state = {isLoading: true,
                  error: false,
                  errorMessage: null,
                  login: '',
                  password: '',
                  logged: false,
                  username: null
    }
    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
  }

  handleChange(event) { 
    this.setState({
      [event.target.id]: event.target.value
    })
  }

  validateForm() {
    return this.state.login.length > 0 && this.state.password.length > 0
  }

  handleSubmit(event) {

    let requestUrl = '/api/login'
    let data = {
      login: this.state.login,
      password: this.state.password
    }

    axios.post(requestUrl, data)
    .then(response => {
      console.log('Login', requestUrl, response.data)
      this.setState({
        isLoading: false,
        error: false,
        errorMessage: null,
        username: response.data.username,
        logged: true
      })
      this.props.setStateNavbar({
        username: this.state.username,
        logged: this.state.logged
      })
    })
    .catch( (error) => {
      console.log(error)
    })
    event.preventDefault()
  }

  render() {
    let html = <Redirect to="/" />
    if (!this.state.logged) {
      html = (
        <div className="container">
          <h1>Login</h1>
          <div className="col-md-4">
            <Form onSubmit={this.handleSubmit}>
              <FormGroup>
                <Label for="login">Email</Label>
                <Input type="text" name="login" id="login" placeholder="login" value={this.state.login} onChange={this.handleChange} />
              </FormGroup>
              <FormGroup>
                <Label for="password">Password</Label>
                <Input type="password" name="password" id="password" placeholder="password" value={this.state.password} onChange={this.handleChange} />
              </FormGroup>
              <Button disabled={!this.validateForm()}>Login</Button>
            </Form>
          </div>
        </div>
      )
    }
    return html
  }
}

