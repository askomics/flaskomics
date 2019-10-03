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
    this.handleNegative = this.props.handleNegative.bind(this)
    this.toggleOptional = this.props.toggleOptional.bind(this)
    this.handleFilterType = this.props.handleFilterType.bind(this)
    this.handleFilterValue = this.props.handleFilterValue.bind(this)
    this.handleFilterCategory = this.props.handleFilterCategory.bind(this)
    this.handleFilterNumericSign = this.props.handleFilterNumericSign.bind(this)
    this.handleFilterNumericValue = this.props.handleFilterNumericValue.bind(this)
    this.toggleLinkAttribute = this.props.toggleLinkAttribute.bind(this)
    this.handleChangeLink = this.props.handleChangeLink.bind(this)
  }

  subNums (id) {
    let newStr = ""
    let oldStr = id.toString()
    let arrayString = [...oldStr]
    arrayString.forEach(char => {
      let code = char.charCodeAt()
      newStr += String.fromCharCode(code + 8272)
    })
    return newStr
  }

  renderLinker () {
    let options = []

    this.props.graph.nodes.map(node => {
      if (!node.suggested) {
        options.push(<option style={{"background-color": "#cccccc"}} disabled>{node.label + " " + this.subNums(node.humanId)}</option>)
        this.props.graph.attr.map(attr => {
          if (attr.id != this.props.attribute.id && attr.nodeId == node.id && attr.type == this.props.attribute.type) {
            options.push(<option key={attr.id} value={attr.id} selected={this.props.attribute.linkedWith == attr.id ? true : false}>{attr.label}</option>)
          }
        })
      }
    })

    return (
        <CustomInput type="select" id={this.props.attribute.id} name="link" onChange={this.handleChangeLink}>
          <option style={{"background-color": "#cccccc"}} disabled selected>{"Link with a " + this.props.attribute.type + " attribute"}</option>
          {options.map(opt => {
            return opt
          })}
        </CustomInput>
      )
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

    let negativIcon = 'attr-icon fas fa-not-equal inactive'
    if (this.props.attribute.negative) {
      negativIcon = 'attr-icon fas fa-not-equal'
    }

    let linkIcon = 'attr-icon fas fa-unlink inactive'
    if (this.props.attribute.linked) {
      linkIcon = 'attr-icon fas fa-link'
    }

    let selected = {
      'exact': false,
      'regexp': false
    }

    let selected_sign = {
      '=': !this.props.attribute.negative,
      "≠": this.props.attribute.negative
    }

    selected[this.props.attribute.filterType] = true

    let form

    if (this.props.attribute.linked) {
      form = this.renderLinker()
    } else {
      form = (
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
              <CustomInput disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleNegative}>
                {Object.keys(selected_sign).map(type => {
                  return <option key={type} selected={selected_sign[type]} value={type}>{type}</option>
                })}
              </CustomInput>
            </td>
            <td>
              <Input disabled={this.props.attribute.optional} type="text" id={this.props.attribute.id} value={this.props.attribute.filterValue} onChange={this.handleFilterValue} />
            </td>
          </tr>
        </table>
      )
    }

    return (
      <div className="attribute-box">
        <label className="attr-label">{this.props.attribute.label}</label>
        <div className="attr-icons">
          {this.props.attribute.uri == "rdf:type" || this.props.attribute.uri == "rdfs:label" ? <nodiv></nodiv> : <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional}></i> }
          <i className={linkIcon} id={this.props.attribute.id} onClick={this.toggleLinkAttribute}></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility}></i>
        </div>
        {form}
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

    let linkIcon = 'attr-icon fas fa-unlink inactive'
    if (this.props.attribute.linked) {
      linkIcon = 'attr-icon fas fa-link'
    }

    let selected = {
      '=': false,
      '<': false,
      '<=': false,
      '>': false,
      '>=': false,
      '!=': false
    }

    let sign_display = {
      '=': '=',
      '<': '<',
      '<=': '≤',
      '>': '>',
      '>=': '≥',
      '!=': '≠'
    }

    selected[this.props.attribute.filterSign] = true

    let form

    if (this.props.attribute.linked) {
      form = this.renderLinker()
    } else {
      form = (
        <table style={{ width: '100%' }}>
          <tr>
            <td>
              <CustomInput disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleFilterNumericSign}>
                {Object.keys(selected).map(sign => {
                  return <option key={sign} selected={selected[sign]} value={sign}>{sign_display[sign]}</option>
                })}
              </CustomInput>
            </td>
            <td>
              <Input disabled={this.props.attribute.optional} type="text" id={this.props.attribute.id} value={this.props.attribute.filterValue} onChange={this.handleFilterNumericValue} />
            </td>
          </tr>
        </table>
      )
    }

    return (
      <div className="attribute-box">
        <label className="attr-label">{this.props.attribute.label}</label>
        <div className="attr-icons">
          <i className={linkIcon} id={this.props.attribute.id} onClick={this.toggleLinkAttribute}></i>
          <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional}></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility}></i>
        </div>
        {form}
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

    let linkIcon = 'attr-icon fas fa-unlink inactive'
    if (this.props.attribute.linked) {
      linkIcon = 'attr-icon fas fa-link'
    }

    let form

    if (this.props.attribute.linked) {
      form = this.renderLinker()
    } else {
      form = (
        <FormGroup>
          <CustomInput disabled={this.props.attribute.optional} style={{ height: '60px' }} className="attr-select" type="select" id={this.props.attribute.id} onChange={this.handleFilterCategory} multiple>
            {this.props.attribute.filterValues.map(value => {
              let selected = this.props.attribute.filterSelectedValues.includes(value.uri)
              return (<option key={value.uri} attrId={this.props.attribute.uri} value={value.uri} selected={selected}>{value.label}</option>)
            })}
          </CustomInput>
        </FormGroup>
      )
    }

    return (
      <div className="attribute-box">
        <label className="attr-label">{this.props.attribute.label}</label>
        <div className="attr-icons">
          <i className={linkIcon} id={this.props.attribute.id} onClick={this.toggleLinkAttribute}></i>
          <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional}></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility}></i>
        </div>
        {form}
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
  handleNegative: PropTypes.func,
  toggleVisibility: PropTypes.func,
  toggleOptional: PropTypes.func,
  handleFilterType: PropTypes.func,
  handleFilterValue: PropTypes.func,
  handleFilterCategory: PropTypes.func,
  handleFilterNumericSign: PropTypes.func,
  handleFilterNumericValue: PropTypes.func,
  toggleLinkAttribute: PropTypes.func,
  handleChangeLink: PropTypes.func,
  attribute: PropTypes.object,
  graph: PropTypes.object
}
