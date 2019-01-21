import React from 'react';
import { Link } from "react-router-dom";

import axios from 'axios'

class Navbar extends React.Component {

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
        'logged': true
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
        <nav className="navbar navbar-expand-md navbar-dark bg-dark">
          <div className="container">
            <div className="navbar-collapse collapse w-100 order-1 order-md-0 dual-collapse2">
              <a className="navbar-brand" href="/">AskOmics</a>
            </div>
            <div className="navbar-collapse collapse w-100 order-3 dual-collapse2">
              <ul className="navbar-nav ml-auto">
                <li className="nav-item">
                  <Link className="nav-link" to="/ask"><i className="fas fa-play"></i> Ask!</Link>
                </li>
                <li className="nav-item">
                  {jobs_link}
                </li>
                <li className="nav-item">
                  {upload_link}
                </li>
                <li className="nav-item">
                  {datasets_link}
                </li>
                <li className="nav-item">
                  {login_link}
                </li>
              </ul>
            </div>
          </div>
        </nav>
        <br />
      </div>
    )
  }
}

export default Navbar;