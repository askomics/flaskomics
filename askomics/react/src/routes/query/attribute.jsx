import React, { Component } from 'react'
import axios from 'axios'
import { Input, FormGroup, CustomInput } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import Visualization from './visualization'
import PropTypes from 'prop-types'

export default class AttributeBox extends Component {
  constructor (props) {
    super(props)
    this.state = {}

    this.toggleVisibility = this.props.toggleVisibility.bind(this)
    this.toggleOptional = this.props.toggleOptional.bind(this)
    this.handleFilterType = this.props.handleFilterType.bind(this)
    this.handleFilterValue = this.props.handleFilterValue.bind(this)
    this.handleFilterCategory = this.props.handleFilterCategory.bind(this)
    this.handleFilterNumericSign = this.props.handleFilterNumericSign.bind(this)
    this.handleFilterNumericValue = this.props.handleFilterNumericValue.bind(this)
  }

  renderText () {
    let eyeIcon = 'attr-icon fas fa-eye-slash inactive'
    if (this.props.attribute.visible) {
      eyeIcon = 'attr-icon fas fa-eye'
    }

    let optionalIcon = 'attr-icon fas fa-question-circle inactive'
    if (this.props.attribute.optional) {
      optionalIcon = 'attr-icon fas fa-question-circle'
    }

    let selected = {
      'exact': false,
      'regexp': false
    }

    selected[this.props.attribute.filterType] = true

    return (
      <div className="attribute-box">
        <label className="attr-label">{this.props.attribute.label}</label>
        <div className="attr-icons">
          {this.props.attribute.uri == "rdf:type" || this.props.attribute.uri == "rdfs:label" ? <nodiv></nodiv> : <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional}></i> }
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility}></i>
        </div>
        <table style={{ width: '100%' }}>
          <tr>
            <td>
              <CustomInput disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleFilterType}>
                {Object.keys(selected).map(type => {
                  return <option key={type} selected={selected[type]} value={type}>{type}</option>
                })}
              </CustomInput>
            </td>
            <td>
              <Input disabled={this.props.attribute.optional} type="text" id={this.props.attribute.id} value={this.props.attribute.filterValue} onChange={this.handleFilterValue} />
            </td>
          </tr>
        </table>
      </div>
    )
  }

  renderNumeric () {
    let eyeIcon = 'attr-icon fas fa-eye-slash inactive'
    if (this.props.attribute.visible) {
      eyeIcon = 'attr-icon fas fa-eye'
    }

    let optionalIcon = 'attr-icon fas fa-question-circle inactive'
    if (this.props.attribute.optional) {
      optionalIcon = 'attr-icon fas fa-question-circle'
    }

    let selected = {
      '=': false,
      '<': false,
      '<=': false,
      '>': false,
      '>=': false,
      '!=': false
    }

    selected[this.props.attribute.filterSign] = true

    return (
      <div className="attribute-box">
        <label className="attr-label">{this.props.attribute.label}</label>
        <div className="attr-icons">
          <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional}></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility}></i>
        </div>
        <table style={{ width: '100%' }}>
          <tr>
            <td>
              <CustomInput disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleFilterNumericSign}>
                {Object.keys(selected).map(sign => {
                  return <option key={sign} selected={selected[sign]} value={sign}>{sign}</option>
                })}
              </CustomInput>
            </td>
            <td>
              <Input disabled={this.props.attribute.optional} type="text" id={this.props.attribute.id} value={this.props.attribute.filterValue} onChange={this.handleFilterNumericValue} />
            </td>
          </tr>
        </table>
      </div>
    )
  }

  renderCategory () {
    let eyeIcon = 'attr-icon fas fa-eye-slash inactive'
    if (this.props.attribute.visible) {
      eyeIcon = 'attr-icon fas fa-eye'
    }

    let optionalIcon = 'attr-icon fas fa-question-circle inactive'
    if (this.props.attribute.optional) {
      optionalIcon = 'attr-icon fas fa-question-circle'
    }

    let categoryFormGroup = (
      <FormGroup>
        <CustomInput disabled={this.props.attribute.optional} style={{ height: '60px' }} className="attr-select" type="select" id={this.props.attribute.id} onChange={this.handleFilterCategory} multiple>
          {this.props.attribute.filterValues.map(value => {
            let selected = this.props.attribute.filterSelectedValues.includes(value.uri)
            return (<option key={value.uri} attrId={this.props.attribute.uri} value={value.uri} selected={selected}>{value.label}</option>)
          })}
        </CustomInput>
      </FormGroup>
    )

    return (
      <div className="attribute-box">
        <label className="attr-label">{this.props.attribute.label}</label>
        <div className="attr-icons">
          <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional}></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility}></i>
        </div>
        {categoryFormGroup}
      </div>
    )
  }

  render () {
    let box = null
    if (this.props.attribute.type == 'text' || this.props.attribute.type == 'uri') {
      box = this.renderText()
    }
    if (this.props.attribute.type == 'decimal') {
      box = this.renderNumeric()
    }
    if (this.props.attribute.type == 'category') {
      box = this.renderCategory()
    }
    return box
  }
}

AttributeBox.propTypes = {
  toggleVisibility: PropTypes.func,
  handleFilterType: PropTypes.func,
  handleFilterValue: PropTypes.func,
  handleFilterCategory: PropTypes.func,
  handleFilterNumericSign: PropTypes.func,
  handleFilterNumericValue: PropTypes.func,
  attribute: PropTypes.object
}
