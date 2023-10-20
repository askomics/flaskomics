import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import { Collapse, Navbar, NavbarBrand, Nav, NavItem } from 'reactstrap'
import PropTypes from 'prop-types'
import Template from './components/template'

export default class Contact extends Component {
  constructor (props) {
    super(props)
    console.log("test")
  }

  render () {
    return (
      <div className="container">
      <h2>Contact</h2>
      <hr />
      <div>
        <Template template={this.props.config.contactMessage}/>
      </div>
      </div>
    )
  }
}

Contact.propTypes = {
  config: PropTypes.object
}
