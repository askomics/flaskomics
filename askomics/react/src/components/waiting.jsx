import React, { Component } from 'react'
import { Spinner } from 'reactstrap'
import PropTypes from 'prop-types'

export default class WaitingDiv extends Component {
  constructor (props) {
    super(props)
    this.state = {
      center: this.props.center ? 'center' : ''
    }
  }

  render () {
    if (this.props.waiting) {
      return (
        <div className={this.state.center}>
          <Spinner color="secondary" />
        </div>
      )
    }
    return null
  }
}

WaitingDiv.propTypes = {
  center: PropTypes.bool,
  waiting: PropTypes.bool
}
