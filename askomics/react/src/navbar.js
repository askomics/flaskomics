import React from 'react';
import { Link } from "react-router-dom";

class Navbar extends React.Component {
  render() {
    return (
      <div>
        <nav class="navbar navbar-expand-md navbar-dark bg-dark">
          <div class="container">
            <div class="navbar-collapse collapse w-100 order-1 order-md-0 dual-collapse2">
              <a class="navbar-brand" href="/">AskOmics</a>
            </div>
            <div class="navbar-collapse collapse w-100 order-3 dual-collapse2">
              <ul class="navbar-nav ml-auto">
                <li class="nav-item">
                  <Link className="nav-link" to="/ask"><i class="fas fa-play"></i> Ask!</Link>
                </li>
                <li class="nav-item">
                  <Link className="nav-link" to="/jobs"><i class="fas fa-tasks"></i> Jobs</Link>
                </li>
                <li class="nav-item">
                  <Link className="nav-link" to="/upload"><i class="fas fa-upload"></i> Upload</Link>
                </li>
                <li class="nav-item">
                  <Link className="nav-link" to="/datasets"><i class="fas fa-database"></i> Datasets</Link>
                </li>
                <li class="nav-item">
                  <Link className="nav-link" to="/login"><i class="fas fa-sign-in-alt"></i> Login</Link>
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