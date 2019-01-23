import React, { Component } from "react"
import { Link } from "react-router-dom";
import { Collapse, Navbar, NavbarBrand, Nav, NavItem } from 'reactstrap';

export default class AskoFooter extends Component {

  constructor(props) {
    super(props)
  }

  render() {
    return (
      <footer className="footer footer-content">
      <div className="container">
          <div className="footer-left">
            AskOmics {this.props.version}
          </div>
          <div className="footer-right">
            {this.props.message}
          </div>
        </div>
      </footer>
    )
  }
}
