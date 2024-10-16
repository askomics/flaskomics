import React, { Component} from 'react'
import axios from 'axios'
import { Input, FormGroup, CustomInput, FormFeedback } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import DatePicker from "react-datepicker";
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'

export default class AttributeBox extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {}

    this.toggleVisibility = this.props.toggleVisibility.bind(this)
    this.handleNegative = this.props.handleNegative.bind(this)
    this.toggleOptional = this.props.toggleOptional.bind(this)
    this.toggleExclude = this.props.toggleExclude.bind(this)
    this.handleFilterType = this.props.handleFilterType.bind(this)
    this.handleFilterValue = this.props.handleFilterValue.bind(this)
    this.handleFilterCategory = this.props.handleFilterCategory.bind(this)
    this.handleFilterNumericSign = this.props.handleFilterNumericSign.bind(this)
    this.handleFilterNumericValue = this.props.handleFilterNumericValue.bind(this)
    this.handleFilterDateValue = this.props.handleFilterDateValue.bind(this)
    this.toggleLinkAttribute = this.props.toggleLinkAttribute.bind(this)
    this.handleChangeLink = this.props.handleChangeLink.bind(this)
    this.toggleAddNumFilter = this.props.toggleAddNumFilter.bind(this)
    this.toggleAddDateFilter = this.props.toggleAddDateFilter.bind(this)
    this.handleDateFilter = this.props.handleDateFilter.bind(this)
    this.handleLinkedNumericModifierSign = this.props.handleLinkedNumericModifierSign.bind(this)
    this.handleLinkedNumericSign = this.props.handleLinkedNumericSign.bind(this)
    this.handleLinkedNumericValue = this.props.handleLinkedNumericValue.bind(this)
    this.toggleAddNumLinkedFilter = this.props.toggleAddNumLinkedFilter.bind(this)
    this.toggleRemoveNumLinkedFilter = this.props.toggleRemoveNumLinkedFilter.bind(this)
    this.handleLinkedNegative = this.props.handleLinkedNegative.bind(this)
    this.handleLinkedFilterValue = this.props.handleLinkedFilterValue.bind(this)
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
    let optionDict = {}
    let content

    this.props.graph.nodes.map(node => {
      if (!node.suggested) {
        options.push(<option style={{"background-color": "#cccccc"}} disabled>{node.label + " " + this.subNums(node.humanId)}</option>)
        this.props.graph.attr.map(attr => {
          if (attr.id != this.props.attribute.id && attr.nodeId == node.id && attr.type == this.props.attribute.type) {
            options.push(<option key={attr.id} value={attr.id} selected={this.props.attribute.linkedWith == attr.id ? true : false} label={attr.label}>{attr.label}</option>)
            optionDict[attr.id] = {label: attr.label, fullLabel: node.label + " " + this.subNums(node.humanId) + " " + attr.label}
          }
        })
      }
    })

    if (this.props.attribute.type == 'text') {
      content = this.renderTextLinker(optionDict)
    }
    if (this.props.attribute.type == 'decimal') {
      content = this.renderNumericLinker(optionDict)
    }
    if (this.props.attribute.type == 'category') {
      content = this.renderBooleanLinker(optionDict)
    }
    if (this.props.attribute.type == 'boolean') {
      content = this.renderBooleanLinker(optionDict)
    }
    if (this.props.attribute.type == 'date') {
      content = this.renderNumericLinker(optionDict, "date")
    }

    let selector

    if (typeof this.props.attribute.linkedWith === "object" && typeof this.props.attribute.linkedWith !== "object"){
      selector = (
        <CustomInput disabled={this.props.attribute.optional || typeof this.props.attribute.linkedWith !== "object"} type="select" id={this.props.attribute.id} name="link" onChange={this.handleChangeLink}>
          <option style={{"background-color": "#cccccc"}} disabled selected>{"Link with a " + this.props.attribute.type + " attribute"}</option>
          {options.map(opt => {
            return opt
          })}
        </CustomInput>
      )
    }

    return (
      <>
      {selector}
      {content}
      </>
    )
  }

  checkUnvalidUri (value) {
    if (value == "") {
      return false
    } else {
      if (value.includes(":")) {
        return false
      } else {
        return !this.utils.isUrl(value)
      }
    }
  }

  renderText () {

    let eyeIcon = 'attr-icon fas fa-eye-slash inactive visibleTooltip'
    if (this.props.attribute.visible) {
      eyeIcon = 'attr-icon fas fa-eye'
    }

    let optionalIcon = 'attr-icon fas fa-question-circle inactive optionalTooltip'
    if (this.props.attribute.optional) {
      optionalIcon = 'attr-icon fas fa-question-circle'
    }

    let negativIcon = 'attr-icon fas fa-not-equal inactive excludeTooltip'
    if (this.props.attribute.negative) {
      negativIcon = 'attr-icon fas fa-not-equal'
    }

    let linkIcon = 'attr-icon fas fa-unlink inactive linkTooltip'
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

    let label = this.props.attribute.displayLabel ?  this.props.attribute.displayLabel : this.props.attribute.label

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
        <label className="attr-label"><Input type="text" id={this.props.attribute.id} placeholder={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} value={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} onChange={this.props.setAttributeName} /></label>
        <div className="attr-icons">
          {this.props.attribute.uri == "rdf:type" || this.props.attribute.uri == "rdfs:label" ? <nodiv></nodiv> : <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional} ></i> }
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility} ></i>
        </div>
        {form}
      </div>
    )
  }

  renderNumeric () {

    let eyeIcon = 'attr-icon fas fa-eye-slash inactive visibleTooltip'
    if (this.props.attribute.visible) {
      eyeIcon = 'attr-icon fas fa-eye'
    }

    let optionalIcon = 'attr-icon fas fa-question-circle inactive optionalTooltip'
    if (this.props.attribute.optional) {
      optionalIcon = 'attr-icon fas fa-question-circle'
    }

    let linkIcon = 'attr-icon fas fa-unlink inactive linkTooltip'
    if (this.props.attribute.linked) {
      linkIcon = 'attr-icon fas fa-link'
    }

    let sign_display = {
      '=': '=',
      '<': '<',
      '<=': '≤',
      '>': '>',
      '>=': '≥',
      '!=': '≠'
    }

    let form
    let numberOfFilters = this.props.attribute.filters.length - 1

    if (this.props.attribute.linked) {
      form = this.renderLinker()
    } else {
      form = (
        <table style={{ width: '100%' }}>
        {this.props.attribute.filters.map((filter, index) => {
          return (
            <tr key={index}>
              <td key={index}>
                <CustomInput key={index} data-index={index} disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleFilterNumericSign}>
                  {Object.keys(sign_display).map(sign => {
                    return <option key={sign} selected={filter.filterSign == sign ? true : false} value={sign}>{sign_display[sign]}</option>
                  })}
                </CustomInput>
              </td>
                <td>
                  <div className="input-with-icon">
                    <Input data-index={index} className="input-with-icon" disabled={this.props.attribute.optional} type="text" id={this.props.attribute.id} value={filter.filterValue} onChange={this.handleFilterNumericValue} />
                    {index == numberOfFilters ? <button className="input-with-icon"><i className="attr-icon fas fa-plus inactive" id={this.props.attribute.id} onClick={this.toggleAddNumFilter}></i></button> : <></>}
                  </div>
                </td>
            </tr>
          )
        })}
        </table>
      )
    }

    return (
      <div className="attribute-box">
        <label className="attr-label"><Input type="text" id={this.props.attribute.id} placeholder={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} value={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} onChange={this.props.setAttributeName} /></label>
        <div className="attr-icons">
          <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional} ></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility} ></i>
        </div>
        {form}
      </div>
    )
  }

  renderCategory () {

    let eyeIcon = 'attr-icon fas fa-eye-slash inactive visibleTooltip'
    if (this.props.attribute.visible) {
      eyeIcon = 'attr-icon fas fa-eye'
    }

    let optionalIcon = 'attr-icon fas fa-question-circle inactive optionalTooltip'
    if (this.props.attribute.optional) {
      optionalIcon = 'attr-icon fas fa-question-circle'
    }

    let linkIcon = 'attr-icon fas fa-unlink inactive linkTooltip'
    if (this.props.attribute.linked) {
      linkIcon = 'attr-icon fas fa-link'
    }

    let excludeIcon = 'attr-icon fas fa-ban inactive excludeTooltip'
    if (this.props.attribute.exclude) {
      excludeIcon = 'attr-icon fas fa-ban'
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
              return (<option key={value.uri} value={value.uri} selected={selected}>{value.label}</option>)
            })}
          </CustomInput>
        </FormGroup>
      )
    }

    return (
      <div className="attribute-box">
        <label className="attr-label"><Input type="text" id={this.props.attribute.id} placeholder={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} value={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} onChange={this.props.setAttributeName} /></label>
        <div className="attr-icons">
          <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional} ></i>
          <i className={excludeIcon} id={this.props.attribute.id} onClick={this.toggleExclude} ></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility} ></i>
        </div>
        {form}
      </div>
    )
  }

  renderBoolean () {

    let eyeIcon = 'attr-icon fas fa-eye-slash inactive visibleTooltip'
    if (this.props.attribute.visible) {
      eyeIcon = 'attr-icon fas fa-eye'
    }

    let optionalIcon = 'attr-icon fas fa-question-circle inactive optionalTooltip'
    if (this.props.attribute.optional) {
      optionalIcon = 'attr-icon fas fa-question-circle'
    }

    let linkIcon = 'attr-icon fas fa-unlink inactive linkTooltip'
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
            <option key="true" value="true" selected={this.props.attribute.filterSelectedValues.includes("true")}>True</option>
            <option key="false" value="false" selected={this.props.attribute.filterSelectedValues.includes("false")}>False</option>
          </CustomInput>
        </FormGroup>
      )
    }

    return (
      <div className="attribute-box">
        <label className="attr-label"><Input type="text" id={this.props.attribute.id} placeholder={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} value={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} onChange={this.props.setAttributeName} /></label>
        <div className="attr-icons">
          <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional} ></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility} ></i>
        </div>
        {form}
      </div>
    )
  }

  renderDate () {

    let eyeIcon = 'attr-icon fas fa-eye-slash inactive visibleTooltip'
    if (this.props.attribute.visible) {
      eyeIcon = 'attr-icon fas fa-eye'
    }

    let optionalIcon = 'attr-icon fas fa-question-circle inactive optionalTooltip'
    if (this.props.attribute.optional) {
      optionalIcon = 'attr-icon fas fa-question-circle'
    }

    let linkIcon = 'attr-icon fas fa-unlink inactive linkTooltip'
    if (this.props.attribute.linked) {
      linkIcon = 'attr-icon fas fa-link'
    }

    let sign_display = {
      '=': '=',
      '<': '<',
      '<=': '≤',
      '>': '>',
      '>=': '≥',
      '!=': '≠'
    }
    let form
    let numberOfFilters = this.props.attribute.filters.length - 1

    if (this.props.attribute.linked) {
      form = this.renderLinker()
    } else {
      form = (
        <table style={{ width: '100%' }}>
        {this.props.attribute.filters.map((filter, index) => {
          return (
            <tr key={index}>
              <td key={index}>
                <CustomInput key={index} data-index={index} disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleDateFilter}>
                  {Object.keys(sign_display).map(sign => {
                    return <option key={sign} selected={filter.filterSign == sign ? true : false} value={sign}>{sign_display[sign]}</option>
                  })}
                </CustomInput>
              </td>
                <td>
                  <div className="input-with-icon">
                    <DatePicker dateFormat="yyyy/MM/dd" disabled={this.props.attribute.optional} id={this.props.attribute.id}
                    selected={typeof filter.filterValue === 'string' ? Date.parse(filter.filterValue) : filter.filterValue}
                    isClearable
                    showMonthDropdown
                    showYearDropdown
                    dropdownMode="select"
                    onChange={(date, event) => {
                        event.target = {value:date, id: this.props.attribute.id, dataset:{index: index}};
                        this.handleFilterDateValue(event)
                    }} />
                    {index == numberOfFilters ? <button className="input-with-icon"><i className="attr-icon fas fa-plus inactive" id={this.props.attribute.id} onClick={this.toggleAddDateFilter}></i></button> : <></>}
                  </div>
                </td>
            </tr>
          )
        })}
        </table>
      )
    }

    return (
      <div className="attribute-box">
        <label className="attr-label"><Input type="text" id={this.props.attribute.id} placeholder={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} value={this.props.attribute.displayLabel ? this.props.attribute.displayLabel : this.props.attribute.label} onChange={this.props.setAttributeName} /></label>
        <div className="attr-icons">
          <i className={optionalIcon} id={this.props.attribute.id} onClick={this.toggleOptional} ></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility} ></i>
        </div>
        {form}
      </div>
    )
  }

  renderNumericLinker (options, type="num"){
    const sign_display = {
      '=': '=',
      '<': '<',
      '<=': '≤',
      '>': '>',
      '>=': '≥',
      '!=': '≠'
    }

    const modifier_display = {
      '+': '+',
      '-': '-',
    }
    let customParams
    const placeholder = type === "num"? "0" : "0 days"
    const numberOfFilters = this.props.attribute.linkedFilters.length - 1

    if (typeof this.props.attribute.linkedWith !== "object") {
      let selectedLabel = options[this.props.attribute.linkedWith.toString()].label
      let fullLabel = options[this.props.attribute.linkedWith.toString()].fullLabel
      customParams = (
        <table style={{ width: '100%' }}>
        {this.props.attribute.linkedFilters.map((filter, index) => {
          return (
            <tr key={index}>
              <td key={index}>
                <CustomInput key={index} data-index={index} disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleLinkedNumericSign}>
                  {Object.keys(sign_display).map(sign => {
                    return <option key={sign} selected={filter.filterSign == sign ? true : false} value={sign}>{sign_display[sign]}</option>
                  })}
                </CustomInput>
              </td>
              <td>
              <Input disabled={true} type="text" value={fullLabel} size={selectedLabel.length}/>
              </td>
              <td>
              <CustomInput key={index} data-index={index} disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleLinkedNumericModifierSign}>
                {Object.keys(modifier_display).map(sign => {
                  return <option key={sign} selected={filter.filterModifier == sign ? true : false} value={sign}>{modifier_display[sign]}</option>
                })}
              </CustomInput>
              </td>
              <td>
                <div className="input-with-icon">
                <Input className="input-with-icon" data-index={index} disabled={this.props.attribute.optional} type="text" id={this.props.attribute.id} value={filter.filterValue} onChange={this.handleLinkedNumericValue} placeholder={placeholder} />
                {index == numberOfFilters ? <button className="input-with-icon"><i className="attr-icon fas fa-plus inactive" id={this.props.attribute.id} onClick={this.toggleAddNumLinkedFilter}></i></button> : <></>}
                {index == numberOfFilters && index > 0 ? <button className="input-with-icon-two"><i className="attr-icon fas fa-minus inactive" id={this.props.attribute.id} onClick={this.toggleRemoveNumLinkedFilter}></i></button> : <></>}
                </div>
              </td>
            </tr>
          )
        })}
        </table>
      )
    }
    return customParams
  }

  renderTextLinker (options){
    let selected_sign = {
      '=': !this.props.attribute.linkedNegative,
      "≠": this.props.attribute.linkedNegative
    }

    let customParams
    const placeholder = "$1"

    if (typeof this.props.attribute.linkedWith !== "object") {
      let selectedLabel = options[this.props.attribute.linkedWith.toString()].label + " as $1"
      let fullLabel = options[this.props.attribute.linkedWith.toString()].fullLabel
      customParams = (
        <table style={{ width: '100%' }}>
          <tr>
            <td>
              <CustomInput disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleLinkedNegative}>
                {Object.keys(selected_sign).map(type => {
                  return <option key={type} selected={selected_sign[type]} value={type}>{type}</option>
                })}
              </CustomInput>
            </td>
            <td>
              <Input disabled={true} type="text" value={fullLabel} size={selectedLabel.length}/>
            </td>
            <td>
              <Input
                className="linkedTooltip"
                disabled={this.props.attribute.optional}
                type="text"
                id={this.props.attribute.id}
                value={this.props.attribute.linkedFilterValue}
                onChange={this.handleLinkedFilterValue}
                placeholder={placeholder}
              />
            </td>
          </tr>
        </table>
      )
    }
    return customParams
  }

  renderBooleanLinker (options, type="num"){
    let selected_sign = {
      '=': !this.props.attribute.linkedNegative,
      "≠": this.props.attribute.linkedNegative
    }

    let customParams
    const placeholder = "$1"

    if (typeof this.props.attribute.linkedWith !== "object") {
      let selectedLabel = options[this.props.attribute.linkedWith.toString()].label
      let fullLabel = options[this.props.attribute.linkedWith.toString()].fullLabel
      customParams = (
        <table style={{ width: '100%' }}>
          <tr>
            <td>
              <CustomInput disabled={this.props.attribute.optional} type="select" id={this.props.attribute.id} onChange={this.handleLinkedNegative}>
                {Object.keys(selected_sign).map(type => {
                  return <option key={type} selected={selected_sign[type]} value={type}>{type}</option>
                })}
              </CustomInput>
            </td>
            <td>
              <Input disabled={true} type="text" value={fullLabel} size={selectedLabel.length}/>
            </td>
          </tr>
        </table>
      )
    }
    return customParams
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
    if (this.props.attribute.type == 'boolean') {
      box = this.renderBoolean()
    }
    if (this.props.attribute.type == 'date') {
      box = this.renderDate()
    }
    return box
  }
}

AttributeBox.propTypes = {
  handleNegative: PropTypes.func,
  toggleVisibility: PropTypes.func,
  toggleOptional: PropTypes.func,
  toggleExclude: PropTypes.func,
  toggleAddNumFilter: PropTypes.func,
  handleFilterType: PropTypes.func,
  handleFilterValue: PropTypes.func,
  handleFilterCategory: PropTypes.func,
  handleFilterNumericSign: PropTypes.func,
  handleFilterNumericValue: PropTypes.func,
  toggleLinkAttribute: PropTypes.func,
  handleChangeLink: PropTypes.func,
  toggleAddDateFilter: PropTypes.func,
  handleFilterDateValue: PropTypes.func,
  handleDateFilter: PropTypes.func,
  attribute: PropTypes.object,
  graph: PropTypes.object,
  setAttributeName: PropTypes.func,
  handleLinkedNumericModifierSign: PropTypes.func,
  handleLinkedNumericSign: PropTypes.func,
  handleLinkedNumericValue: PropTypes.func,
  toggleAddNumLinkedFilter: PropTypes.func,
  toggleRemoveNumLinkedFilter: PropTypes.func,
  handleLinkedNegative: PropTypes.func,
  handleLinkedFilterValue: PropTypes.func
}
