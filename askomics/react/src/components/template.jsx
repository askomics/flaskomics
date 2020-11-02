import React, { Component } from 'react'
import PropTypes from 'prop-types'

export default class Template extends Component {

  constructor(props) {
    super(props)
  }

  render() {
    return <div dangerouslySetInnerHTML={{__html: this.props.template}}/>
  }
}

Template.propTypes = {
  template: PropTypes.string.isRequired
}
