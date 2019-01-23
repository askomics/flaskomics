import React from 'react';
import { Link } from "react-router-dom";
import { Collapse, Navbar, NavbarBrand, Nav, NavItem } from 'reactstrap';
import axios from 'axios'

export default  class AskoNavbar extends React.Component {

  constructor(props) {
    super(props)
  }

  render() {

    let links = (
      <NavItem><Link className="nav-link" to="/login"><i className="fas fa-sign-out-alt"></i> Login</Link></NavItem>
    )

    if(this.props.logged) {
      links = (
        <>
        <NavItem><Link className="nav-link" to="/jobs"><i className="fas fa-tasks"></i> Jobs</Link></NavItem>
        <NavItem><Link className="nav-link" to="/upload"><i className="fas fa-upload"></i> Upload</Link></NavItem>
        <NavItem><Link className="nav-link" to="/datasets"><i className="fas fa-database"></i> Datasets</Link></NavItem>
        <NavItem><Link className="nav-link" to="/logout"><i className="fas fa-sign-in-alt"></i> Logout ({this.props.username})</Link></NavItem>
        </>
      )
    }

    return (
      <div>
        <Navbar color="dark" dark expand="md">
          <div className="container">
            <NavbarBrand href="/">AskOmics</NavbarBrand>
            <Collapse navbar>
              <Nav className="ml-auto" navbar>
                <NavItem>
                  <Link className="nav-link" to="/"><i className="fas fa-play"></i> Ask!</Link>
                </NavItem>
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
