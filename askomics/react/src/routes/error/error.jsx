import React, { Component } from "react"
import { Alert } from 'reactstrap'
import { Redirect} from 'react-router'

export default class ErrorDiv extends Component {

  constructor(props) {
    super(props)
  }

  render() {
    if (this.props.status == 401) {
      return <Redirect to="/login" />
    }

    if (!this.props.error) {
      return null
    }


    let error
    if (Array.isArray(this.props.errorMessage)) {
      error = (
        <Alert color="danger">
        {this.props.errorMessage.map((item, index) => (
          <div key={index}><i className="fas fa-exclamation-circle"></i> {item}</div>
        ))}
        </Alert>
      )
    }else{
      error = (
        <Alert color="danger">
          <div><i className="fas fa-exclamation-circle"></i> {this.props.errorMessage}</div>
        </Alert>
      )
    }

    return (
      <div>
        {error}
      </div>
    )
  }
}
