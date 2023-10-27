import React, { Component } from 'react'
import axios from 'axios'
import { Input, FormGroup, CustomInput, Col, Row, Button } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import Visualization from './visualization'
import PropTypes from 'prop-types'

export default class OntoLinkView extends Component {
  constructor (props) {
    super(props)
    this.handleRecursiveOntology = this.props.handleRecursiveOntology.bind(this)
  }

  render () {

    return (
      <div className="container">
        <h5>Ontological Relation</h5>
        <hr />
        <CustomInput disabled={!this.props.link.isRecursive} onChange={this.handleRecursiveOntology} checked={this.props.link.recursive ? true : false} value={this.props.link.recursive ? true : false} type="checkbox" id={"recursive-" + this.props.link.id} label="Recursive" />
        <br />
      </div>
    )
  }
}

OntoLinkView.propTypes = {
  link: PropTypes.object,
  handleRecursiveOntology: PropTypes.func
}
