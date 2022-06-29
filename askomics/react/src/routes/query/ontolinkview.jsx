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
                <option selected={this.props.link.uri == 'http://www.w3.org/2000/01/rdf-schema#subClassOf' ? true : false} value="http://www.w3.org/2000/01/rdf-schema#subClassOf">children of</option>
                <option selected={this.props.link.uri == 'http://www.w3.org/2000/01/rdf-schema#subClassOf*' ? true : false} value="http://www.w3.org/2000/01/rdf-schema#subClassOf*">descendants of</option>
                <option selected={this.props.link.uri == '^http://www.w3.org/2000/01/rdf-schema#subClassOf' ? true : false} value="^http://www.w3.org/2000/01/rdf-schema#subClassOf">parents of</option>
                <option selected={this.props.link.uri == '^http://www.w3.org/2000/01/rdf-schema#subClassOf*' ? true : false} value="^http://www.w3.org/2000/01/rdf-schema#subClassOf*">ancestors of</option>
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
