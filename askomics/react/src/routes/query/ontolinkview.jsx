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
    this.handleChangeOntologyType = this.props.handleChangeOntologyType.bind(this)
  }


  render () {
    return (
      <div className="container">
        <h5>Ontological Relation</h5>
        <hr />
        <p>Search on ...</p>
        <table>
          <tr>
            <td>
             <CustomInput type="select" id={this.props.link.id} name="ontology_position" onChange={this.handleChangeOntologyType}>
                <option selected={this.props.link.uri == 'specific' ? true : false} value="specific">a specific</option>
                <option selected={this.props.link.uri == 'children' ? true : false} value="children">children of</option>
                <option selected={this.props.link.uri == 'descendants' ? true : false} value="descendants">descendants of</option>
                <option selected={this.props.link.uri == 'parents' ? true : false} value="parents">parents of</option>
                <option selected={this.props.link.uri == 'ancestors' ? true : false} value="ancestors">ancestors of</option>
              </CustomInput>
            </td>
            <td> a term</td>
          </tr>
        </table>
        <br />
      </div>
    )
  }
}

OntoLinkView.propTypes = {
  link: PropTypes.object,
  handleChangeOntologyType: PropTypes.func,
}
