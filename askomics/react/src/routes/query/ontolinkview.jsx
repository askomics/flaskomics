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
    this.handleReversibleOntology = this.props.handleReversibleOntology.bind(this)
    this.handleRecursiveOntology = this.props.handleRecursiveOntology.bind(this)
  }

  render () {

    return (
      <div className="container">
        <h5>Ontological Relation</h5>
        <hr />
        <CustomInput disabled={!this.props.link.isReversible} onChange={this.handleReversibleOntology} checked={this.props.link.reversible ? true : false} value={this.props.link.reversible ? true : false} type="checkbox" id={"reversible-" + this.props.link.id} label="Reversible" />
        <CustomInput disabled={!this.props.link.isRecursive} onChange={this.handleRecursiveOntology} checked={this.props.link.recursive ? true : false} value={this.props.link.recursive ? true : false} type="checkbox" id={"recursive-" + this.props.link.id} label="Recursive" />
        <br />
      </div>
    )
  }
}

OntoLinkView.propTypes = {
  link: PropTypes.object,
  handleReversibleOntology: PropTypes.func,
  handleRecursiveOntology: PropTypes.func
}
