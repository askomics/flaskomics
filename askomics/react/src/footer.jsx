import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import { Collapse, Navbar, NavbarBrand, Nav, NavItem } from 'reactstrap'
import PropTypes from 'prop-types'

export default class AskoFooter extends Component {
  constructor (props) {
    super(props)
  }

  render () {
    // FIXME: don't hardcode github url
      let commitLink
      if (this.props.commit) {
        commitLink = (<>- <a href={"https://github.com/xgaia/flaskomics/commit/" + this.props.commit}>{this.props.commit}</a></>)
      }
    return (
      <footer className="footer footer-content">
        <div className="container">
          <div className="footer-left">
            AskOmics {this.props.version} {commitLink}
          </div>
          <div className="footer-right">
            {this.props.message}
          </div>
        </div>
      </footer>
    )
  }
}

AskoFooter.propTypes = {
  version: PropTypes.string,
  message: PropTypes.string,
  commit: PropTypes.string
}
