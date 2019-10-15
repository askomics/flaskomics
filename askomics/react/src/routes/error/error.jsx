import React, { Component } from 'react'
import { Alert } from 'reactstrap'
import { Redirect } from 'react-router'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'

export default class ErrorDiv extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
  }

  render () {
    if (this.props.status == 401) {
      return <Redirect to="/login" />
    }

    if (!this.props.error) {
      return null
    }

    let messages = {
      "404": this.utils.objectHaveKeys(this.props, "customMessages", "404") ? this.props.customMessages["404"] : "404 Not Found",
      "503": this.utils.objectHaveKeys(this.props, "customMessages", "503") ? this.props.customMessages["503"] : "503 Service Unavailable ",
      "504": this.utils.objectHaveKeys(this.props, "customMessages", "504") ? this.props.customMessages["504"] : "504 Gateway Time-out",
      "500": this.utils.objectHaveKeys(this.props, "customMessages", "500") ? this.props.customMessages["500"] : this.props.errorMessage ? this.props.errorMessage : "500 Internal Server Error",
    }

    let errorMessage = this.props.errorMessage
    if (this.utils.objectHaveKeys(this.props, "status")) {
      errorMessage = messages[this.props.status.toString()]
    }

    let error
    if (Array.isArray(errorMessage)) {
      error = (
        <Alert color="danger">
          {errorMessage.map((item, index) => (
            <div key={index}><i className="fas fa-exclamation-circle"></i> {item}</div>
          ))}
        </Alert>
      )
    } else {
      error = (
        <Alert color="danger">
          <div><i className="fas fa-exclamation-circle"></i> {errorMessage}</div>
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

ErrorDiv.propTypes = {
  status: PropTypes.number,
  error: PropTypes.bool,
  errorMessage: PropTypes.string
}
