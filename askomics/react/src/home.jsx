import React, { Component } from "react"

import AskoNavbar from './navbar'

export default class Home extends Component {

  constructor(props) {
    super(props)
  }

  render() {
    return (
      <div>
        <AskoNavbar />
        Hello
      </div>
    )
  }
}
