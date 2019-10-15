import React, { Component } from 'react'
import { Alert } from 'reactstrap'
import { Redirect } from 'react-router'
import PropTypes from 'prop-types'

export default class ErrorDiv extends Component {
  constructor (props) {
    super(props)
  }

  render () {
    if (this.props.status == 401) {
      return <Redirect to="/login" />
    }

    if (!this.props.error) {
      return null
    }


    let errorMessage = this.props.errorMessage
    if (this.props.status == 404) {
      errorMessage = "404 not found"
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
