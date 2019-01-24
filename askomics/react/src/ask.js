import React, { Component } from "react"
import axios from 'axios'

export default class Ask extends Component {

  constructor(props) {
    super(props)
    this.state = {
      error: false,
      errorMessage: null,
      logged: props.logged,
      user: props.user
    }
  }

  componentDidMount() {

    let requestUrl = '/api/hello'
    axios.get(requestUrl)
    .then(response => {
      console.log('Ask', requestUrl, response.data)
      this.setState({
        'message': response.data.message
      })
    })
    .catch( (error) => {
      console.log(error)
    })
  }

  render() {
    return (
      <div className="container">
        <h2>Ask!</h2>
        <hr />
        <p>{this.state.message}</p>
      </div>
    )
  }
}
