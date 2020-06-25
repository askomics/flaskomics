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

      "501": this.utils.objectHaveKeys(this.props, "customMessages", "501") ? this.props.customMessages["501"] : "501 Not Implemented",
      "502": this.utils.objectHaveKeys(this.props, "customMessages", "502") ? this.props.customMessages["502"] : "502 Bad Gateway",
      "503": this.utils.objectHaveKeys(this.props, "customMessages", "503") ? this.props.customMessages["503"] : "503 Service Unavailable",
      "504": this.utils.objectHaveKeys(this.props, "customMessages", "504") ? this.props.customMessages["504"] : "504 Gateway Time-out",
      "505": this.utils.objectHaveKeys(this.props, "customMessages", "505") ? this.props.customMessages["505"] : "505 HTTP Version not supported",
      "506": this.utils.objectHaveKeys(this.props, "customMessages", "506") ? this.props.customMessages["506"] : "506 Variant Also Negotiates",
      "507": this.utils.objectHaveKeys(this.props, "customMessages", "507") ? this.props.customMessages["507"] : "507 Insufficient storage",
      "508": this.utils.objectHaveKeys(this.props, "customMessages", "508") ? this.props.customMessages["508"] : "508 Loop detected",
      "509": this.utils.objectHaveKeys(this.props, "customMessages", "509") ? this.props.customMessages["509"] : "509 Bandwidth Limit Exceeded",
      "510": this.utils.objectHaveKeys(this.props, "customMessages", "510") ? this.props.customMessages["510"] : "510 Not extended",
      "511": this.utils.objectHaveKeys(this.props, "customMessages", "511") ? this.props.customMessages["511"] : "511 Network authentication required",

      "500": this.utils.objectHaveKeys(this.props, "customMessages", "500") ? this.props.customMessages["500"] : this.props.errorMessage ? this.props.errorMessage : "500 Internal Server Error",
      "200": this.props.errorMessage
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
    } else {
      error = (
        <Alert color="danger">
          <div><i className="fas fa-exclamation-circle"></i> {messages[this.props.status.toString()]}</div>
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
  errorMessage: PropTypes.array,
  customMessages: PropTypes.object
}
