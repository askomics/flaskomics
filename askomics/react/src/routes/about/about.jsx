import React, { Component } from 'react'
import Template from '../../components/template'
import axios from 'axios'
import DOMPurify from 'dompurify'

export default class About extends Component {
  constructor (props) {
    super(props)
    this.state = {
      about: ""
    }
  }

  componentDidMount() {
    // load about.html page
    let requestUrl = 'static/about.html'
    axios.get(requestUrl).then(response => {
      this.setState({
        about: DOMPurify.sanitize(response.data)
      })
    })
  }

  render () {
    return (
      <div className="container">
        <Template template={this.state.about}/>
      </div>
    )
  }
}
