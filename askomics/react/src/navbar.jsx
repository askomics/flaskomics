import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import { Collapse, Navbar, NavbarBrand, Nav, NavItem, Dropdown, DropdownMenu, DropdownToggle, DropdownItem } from 'reactstrap'
import PropTypes from 'prop-types'

export default class AskoNavbar extends Component {
  constructor (props) {
    super(props)
    this.toggle = this.toggle.bind(this)
    this.state = {
      dropdownOpen: false
    }
  }

  toggle () {
    this.setState({
      dropdownOpen: !this.state.dropdownOpen
    })
  }

  render () {
    let links
    let askLink
    let aboutLink

    // if wait is false
    if (!this.props.waitForStart) {
      askLink = (
        <NavItem><Link className="nav-link" to="/"><i className="fas fa-play"></i> Ask!</Link></NavItem>
      )

      links = (
        <>
          <NavItem><Link className="nav-link" to="/about"><i className="fas fa-info"></i> About</Link></NavItem>
          <NavItem><Link className="nav-link" to="/login"><i className="fas fa-sign-in-alt"></i> Login</Link></NavItem>
        </>
      )


      if (this.props.logged) {
        let adminLinks
        if (this.props.user.admin) {
          adminLinks = (
            <DropdownItem className="bg-dark" tag="Link">
              <Link className="nav-link" to="/admin"><i className="fas fa-chess-king"></i> Admin</Link>
            </DropdownItem>
          )
        }
        let integrationLinks
        if (!this.props.disableIntegration || this.props.user.admin) {
          integrationLinks = (
            <>
            <NavItem><Link className="nav-link" to="/files"><i className="fas fa-file"></i> Files</Link></NavItem>
            <NavItem><Link className="nav-link" to="/datasets"><i className="fas fa-database"></i> Datasets</Link></NavItem>
            </>
          )
        }
        links = (
          <>
          <NavItem><Link className="nav-link" to="/results"><i className="fas fa-tasks"></i> Results</Link></NavItem>
          {integrationLinks}
          <NavItem><Link className="nav-link" to="/about"><i className="fas fa-info"></i> About</Link></NavItem>
          <NavItem>
            <Dropdown nav isOpen={this.state.dropdownOpen} toggle={this.toggle}>
              <DropdownToggle nav caret>
                <i className="fas fa-user"></i> {this.props.user.fname} {this.props.user.lname}
              </DropdownToggle>
              <DropdownMenu className="bg-dark">
                <DropdownItem className="bg-dark" tag="Link">
                  <Link className="nav-link" to="/account"><i className="fas fa-cog"></i> Account managment</Link>
                </DropdownItem>
                {adminLinks}
                <DropdownItem className="bg-dark" divider />
                <DropdownItem className="bg-dark" tag="Link">
                  <Link className="nav-link" to="/logout"><i className="fas fa-sign-out-alt"></i> Logout</Link>
                </DropdownItem>
              </DropdownMenu>
            </Dropdown>
          </NavItem>
          </>
        )
      }
    }

    return (
      <div>
        <Navbar color="dark" dark expand="md">
          <div className="container">
            <NavbarBrand href="/">AskOmics</NavbarBrand>
            <Collapse navbar>
              <Nav className="ml-auto" navbar>
                {askLink}
                {links}
              </Nav>
            </Collapse>
          </div>
        </Navbar>
        <br />
      </div>
    )
  }
}

AskoNavbar.propTypes = {
  waitForStart: PropTypes.bool,
  disableIntegration: PropTypes.bool,
  logged: PropTypes.bool,
  user: PropTypes.object
}