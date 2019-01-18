import React, { Component } from "react";
import axios from 'axios'

export default class Home extends Component {

  constructor(props) {
    super(props)
    this.state = {'isLoading': true, error: false, 'errorMessage': null}
  }

  componentDidMount() {

    let requestUrl = '/api/hello'
    axios.get(requestUrl)
    .then(response => {
        console.log("response", response.data)
        this.setState({
            'isLoading': false,
            'error': false,
            'errorMessage': null,
            'message': response.data.message
        })
    })
    .catch( (error) => {
        console.log(error)
    });

  }

  render() {
    return (
      <div className="container">
          <h1>Hello</h1>
          <p>{this.state.message}</p>
        </div>
    );
  }
}
