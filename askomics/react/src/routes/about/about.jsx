import React, { Component } from 'react'
import Template from '../../components/template'

import htmlTemplate from '../../../../static/about.html'

export default class About extends Component {
  constructor (props) {
    super(props)
  }

  render () {
    return  <Template template={htmlTemplate}/>
  }
}
