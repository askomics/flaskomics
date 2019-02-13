import React, { Component } from "react"
import { Spinner } from "reactstrap"

export default class WaitingDiv extends Component {

  constructor(props) {
    super(props)
    this.state = {
      center: this.props.center ? "center" : ""
    }
  }

  render() {
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
