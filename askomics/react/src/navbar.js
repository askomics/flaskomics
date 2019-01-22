import React from 'react';
import { Link } from "react-router-dom";
import { Collapse, Navbar, NavbarBrand, Nav, NavItem } from 'reactstrap';
import axios from 'axios'

class AskoNavbar extends React.Component {

  constructor(props) {
    super(props)
    this.state = {'isLoading': true,
                  'error': false,
                  'errorMessage': null
    }
  }

  componentDidMount() {

    let requestUrl = '/api/user'
    axios.get(requestUrl)
    .then(response => {
      console.log("response", response.data)
      this.setState({
        'isLoading': false,
        'error': false,
        'errorMessage': null,
        'username': response.data.username,
        'logged': response.data.logged
      })
    })
    .catch( (error) => {
      console.log(error)
    });

  }

  render() {

    let login_link
    let jobs_link
    let upload_link
    let datasets_link
    if(this.state.logged) {
      login_link = <Link className="nav-link" to="/logout"><i className="fas fa-sign-in-alt"></i> Logout</Link>
      jobs_link = <Link className="nav-link" to="/jobs"><i className="fas fa-tasks"></i> Jobs</Link>
      upload_link = <Link className="nav-link" to="/upload"><i className="fas fa-upload"></i> Upload</Link>
      datasets_link = <Link className="nav-link" to="/datasets"><i className="fas fa-database"></i> Datasets</Link>
    }else {
      login_link = <Link className="nav-link" to="/login"><i className="fas fa-sign-out-alt"></i> Login</Link>
    }

    return (
      <div>
        <Navbar color="dark" dark expand="md">
          <div className="container">
            <NavbarBrand href="/">AskOmics</NavbarBrand>
            <Collapse navbar>
              <Nav className="ml-auto" navbar>
                <NavItem>
                  <Link className="nav-link" to="/ask"><i className="fas fa-play"></i> Ask!</Link>
                </NavItem>
                <NavItem>
                  {jobs_link}
                </NavItem>
                <NavItem>
                  {upload_link}
                </NavItem>
                <NavItem>
                  {datasets_link}
                </NavItem>
                <NavItem>
                  {login_link}
                </NavItem>
              </Nav>
            </Collapse>
          </div>
        </Navbar>
        <br />
      </div>
    )
  }
}

export default AskoNavbar
