import React, { Component } from 'react'
import axios from 'axios'
import { Input, FormGroup, CustomInput, Col, Row, Button } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import Visualization from './visualization'
import PropTypes from 'prop-types'

export default class LinkView extends Component {
  constructor (props) {
    super(props)
    this.handleChangePosition = this.props.handleChangePosition.bind(this)
    this.handleClickReverse = this.props.handleClickReverse.bind(this)
    this.handleChangeSameRef = this.props.handleChangeSameRef.bind(this)
    this.handleChangeSameStrand = this.props.handleChangeSameStrand.bind(this)
    this.handleChangeStrict = this.props.handleChangeStrict.bind(this)
    this.nodesHaveRefs = this.props.nodesHaveRefs.bind(this)
    this.nodesHaveStrands = this.props.nodesHaveStrands.bind(this)

  }


  render () {
    return (
      <div className="container">
        <h5>Relation</h5>
        <hr />
        <table>
          <tr>
            <td>{this.props.link.source.label}</td>
            <td>
             <CustomInput type="select" id={this.props.link.id} name="position" onChange={this.handleChangePosition}>
                <option selected={this.props.link.uri == 'included_in' ? true : false} value="included_in">included in</option>
                <option selected={this.props.link.uri == 'overlap_with' ? true : false} value="overlap_with">overlap with</option>
              </CustomInput>
            </td>
            <td>{this.props.link.target.label}</td>
            <td>{"  "}</td>
            <td><Button id={this.props.link.id} color="secondary" size="sm" onClick={this.handleClickReverse}><i className="fas fa-exchange-alt"></i> Reverse</Button></td>
          </tr>
        </table>
        <br />
        <h5>On the same</h5>
        <hr />
        <CustomInput disabled={!this.nodesHaveRefs(this.props.link)} onChange={this.handleChangeSameRef} checked={this.props.link.sameRef ? true : false} value={this.props.link.sameRef ? true : false} type="checkbox" id={"sameref-" + this.props.link.id} label="Same reference" />
        <CustomInput disabled={!this.nodesHaveStrands(this.props.link)} onChange={this.handleChangeSameStrand} checked={this.props.link.sameStrand ? true : false} value={this.props.link.sameStrand ? true : false} type="checkbox" id={"samestrand-" + this.props.link.id} label="Same strand" />
        <hr />
        <br />
        <CustomInput onChange={this.handleChangeStrict} checked={this.props.link.strict ? true : false} value={this.props.link.strict ? true : false} type="checkbox" id={"strict-" + this.props.link.id} label="Strict" />
      </div>
    )
  }
}

LinkView.propTypes = {
  link: PropTypes.object,
  handleChangePosition: PropTypes.func,
  handleClickReverse: PropTypes.func,
  handleChangeSameRef: PropTypes.func,
  handleChangeSameStrand: PropTypes.func,
  handleChangeStrict: PropTypes.func,
  nodesHaveRefs: PropTypes.func,
  nodesHaveStrands: PropTypes.func
}