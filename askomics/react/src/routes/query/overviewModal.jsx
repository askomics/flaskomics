import React, { Component} from 'react'
import { Badge, Button, Modal, ModalHeader, ModalBody, ModalFooter, ButtonGroup, Input, CustomInput, FormGroup } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ReactTooltip from "react-tooltip";
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'

export default class OverviewModal extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      modal: false,
    }
    this.toggleModal = this.toggleModal.bind(this)
    this.handleNodeSelection = this.props.handleNodeSelection.bind(this)
    this.handleLinkSelection = this.props.handleLinkSelection.bind(this)
    this.selectNode = this.selectNode.bind(this)
    this.isSpecialLink = this.isSpecialLink.bind(this)
  }


  selectNode (event){
    let node = this.props.graphState.nodes.find(node => node.id == event.target.id)
    this.toggleModal()

    if (! node.selected){
      this.handleNodeSelection(node)
    }
  }

  isSpecialLink (nodeId){
    let isSpecial = this.props.graphState.links.some(link => {
      return !link.suggested && (link.source.id == nodeId || link.target.id == nodeId) && (link.type == "posLink" || link.type == "ontoLink")
    })

    if(isSpecial){
      return <Badge color="info" className="specialTooltip">Special</Badge>
    }
  }

  toggleModal () {
    this.setState({
      modal: !this.state.modal
    })
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

  renderLinker (attribute) {
    const linked = this.props.graphState.attr.find(attr => attr.id == attribute.linkedWith);
    let content

    if (attribute.type == 'text') {
      content = this.renderTextLinker(attribute, linked.displayLabel)
    }
    if (attribute.type == 'decimal') {
      content = this.renderNumericLinker(attribute, linked.displayLabel)
    }
    if (attribute.type == 'category') {
      content = this.renderBooleanLinker(attribute, linked.displayLabel)
    }
    if (attribute.type == 'boolean') {
      content = this.renderBooleanLinker(attribute, linked.displayLabel)
    }
    if (attribute.type == 'date') {
      content = this.renderNumericLinker(attribute, linked.displayLabel)
    }

    return (
      <>
      <Input value={linked.displayLabel} type="select" disabled>
        <option selected>{linked.displayLabel}</option>
      </Input>
      {content}
      </>
    )
  }

  renderIcons(attribute){

    if (!(attribute.form || attribute.visible || attribute.optional || attribute.linked || attribute.exclude)){
      return false
    }

    let formIcon
    if (attribute.form) {
      formIcon = 'attr-icon fas fa-bookmark '
    }

    let eyeIcon
    if (attribute.visible) {
      eyeIcon = 'attr-icon fas fa-eye'
    }

    let optionalIcon
    if (attribute.optional) {
      optionalIcon = 'attr-icon fas fa-question-circle'
    }

    let linkIcon
    if (attribute.linked) {
      linkIcon = 'attr-icon fas fa-link'
    }

    let excludeIcon
    if (attribute.exclude) {
      excludeIcon = 'attr-icon fas fa-ban'
    }
    return (
      <div className="attr-icons">
        {formIcon ? <i className={formIcon}></i> : <nodiv></nodiv>}
        {linkIcon ? <i className={linkIcon}></i> : <nodiv></nodiv>}
        {optionalIcon ? <i className={optionalIcon}></i> : <nodiv></nodiv>}
        {excludeIcon ? <i className={excludeIcon}></i> : <nodiv></nodiv>}
        {eyeIcon ? <i className={eyeIcon}></i> : <nodiv></nodiv>}
      </div>
    )
  }

  renderTextField (attribute){
    if (attribute.linked && attribute.linkedWith){
      return this.renderLinker(attribute)
    }

    if (!attribute.filterValue){
      return false
    }

    if (attribute.optional){
      return false
    }

    let selected_sign = attribute.negative ? "≠" : '='

    return (
      <table style={{ width: '100%' }}>
        <tr>
          <td>
            <Input type="select" disabled>
              <option selected>{attribute.filterType}</option>
            </Input>
          </td>
          <td>
            <Input type="select" disabled>
              <option selected>{selected_sign}</option>
            </Input>
          </td>
          <td>
            <Input disabled value={attribute.filterValue}/>
          </td>
        </tr>
      </table>
    )
  }

  renderCatField (attribute){
    if (attribute.linked && attribute.linkedWith){
      return this.renderLinker(attribute)
    }

    if (attribute.filterSelectedValues.length == 0){
      return false
    }

    if (attribute.optional){
      return false
    }

    return (
      <FormGroup>
        <Input disabled style={{ height: '60px' }} className="attr-select" type="select" multiple>
          {attribute.filterValues.filter(val => attribute.filterSelectedValues.includes(val.uri)).map(value => {
            return (<option key={value.uri} selected>{value.label}</option>)
          })}
        </Input>
      </FormGroup>
    )
  }

  renderNumField(attribute){
    if (attribute.linked && attribute.linkedWith){
      return this.renderLinker(attribute)
    }

    if (!attribute.filters.some(filter => {return filter.filterValue})){
      return false
    }

    if (attribute.optional){
      return false
    }

    let sign_display = {
      '=': '=',
      '<': '<',
      '<=': '≤',
      '>': '>',
      '>=': '≥',
      '!=': '≠'
    }

    return (
      <table style={{ width: '100%' }}>
      {attribute.filters.map((filter, index) => {
        return (
          <tr key={index}>
            <td key={index}>
              <Input key={index} data-index={index} disabled type="select" id={attribute.id}>
                  <option selected>{sign_display[filter.filterSign]}</option>
              </Input>
            </td>
              <td>
              <Input disabled value={filter.filterValue}/>
              </td>
          </tr>
        )
      })}
      </table>
    )
  }

  attrOverview(attribute){
    let icons = this.renderIcons(attribute)
    let form
    if (attribute.type == 'text' || attribute.type == 'uri') {
      form = this.renderTextField(attribute)
    }
    if (attribute.type == 'decimal' || attribute.type == 'date') {
      form = this.renderNumField(attribute)
    }
    if (attribute.type == 'category' || attribute.type == 'boolean') {
      form = this.renderCatField(attribute)
    }

    if (!(form || icons)){
      return
    }

    return (
      <div className="attribute-box">
        <label className="attr-label">{attribute.label}</label>
        {icons}
        {form}
      </div>
    )
  }

  renderOverview(){
    let data = this.props.graphState.attr.reduce((acc, attr) => {
      let form = this.attrOverview(attr)
      if (form){
        let key = attr.entityDisplayLabel + " " + this.subNums(attr.humanNodeId)
        if (acc[key]){
          acc[key].form.push(form)
        } else {
          acc[key] = {nodeId: attr.nodeId, form:[form]}
        }
      }
      return acc
    }, {})

    return Object.entries(data).map(([key, value]) => {
      return (
        <>
        <div className="entity-box">
          <div className="attr-icons"><Button size="sm" id={value.nodeId} onClick={this.selectNode}>Select entity</Button></div>
          <label className="attr-label">Entity <i>{key}</i> {this.isSpecialLink(value.nodeId)}</label>
          {value.form}
        </div>
        <hr/>
        </>
      )
    })
  }

  renderNumericLinker (attribute, selectedLabel){
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

    if (typeof attribute.linkedWith !== "object") {
      customParams = (
        <table style={{ width: '100%' }}>
        {attribute.linkedFilters.map((filter, index) => {
          return (
            <tr key={index}>
              <td key={index}>
                <CustomInput key={index} data-index={index} disabled={true} type="select" id={attribute.id}>
                  <option key={filter.filterSign} selected={true}>{sign_display[filter.filterSign]}</option>
                </CustomInput>
              </td>
              <td>
              <Input disabled={true} type="text" value={selectedLabel} size={selectedLabel.length}/>
              </td>
              <td>
              <CustomInput key={index} data-index={index} disabled={true} type="select" id={attribute.id}>
                  <option key={filter.filterModifier} selected={true}>{modifier_display[filter.filterModifier]}</option>
              </CustomInput>
              </td>
              <td>
                <div className="input-with-icon">
                <Input className="input-with-icon" data-index={index} disabled={true} type="text" id={attribute.id} value={filter.filterValue}/>
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

  renderTextLinker (attribute, selectedLabel){
    let selected_sign = attribute.linkedNegative ? "≠" : '='
    let customParams

    if (typeof attribute.linkedWith !== "object") {
      customParams = (
        <table style={{ width: '100%' }}>
          <tr>
            <td>
              <CustomInput disabled={true} type="select" id={attribute.id}>
                  <option key={selected_sign} selected={true}>{selected_sign}</option>
              </CustomInput>
            </td>
            <td>
              <Input disabled={true} type="text" value={selectedLabel} size={selectedLabel.length}/>
            </td>
            <td>
              <Input
                disabled={true}
                type="text"
                id={attribute.id}
                value={attribute.linkedFilterValue}
              />
            </td>
          </tr>
        </table>
      )
    }
    return customParams
  }

  renderBooleanLinker (attribute, selectedLabel){
    let selected_sign = attribute.linkedNegative ? "≠" : '='

    let customParams
    const placeholder = "$1"

    if (typeof attribute.linkedWith !== "object") {
      customParams = (
        <table style={{ width: '100%' }}>
          <tr>
            <td>
              <CustomInput disabled={true} type="select" id={attribute.id}>
                <option key={selected_sign} selected={true}>{selected_sign}</option>
              </CustomInput>
            </td>
            <td>
              <Input disabled={true} type="text" value={selectedLabel} size={selectedLabel.length}/>
            </td>
          </tr>
        </table>
      )
    }
    return customParams
  }


  render () {
    let tooltips = (
        <ReactTooltip id="specialTooltip">This node has an active faldo or ontological link</ReactTooltip>
    )
    return(
      <>
      <Button color="info" onClick={this.toggleModal}><i className="fas fa-info"></i> Overview</Button>
      <Modal isOpen={this.state.modal} toggle={this.toggleModal}>
        <ModalHeader toggle={this.toggleModal}>Query overview</ModalHeader>
        <ModalBody style={{ display: 'block', height: this.props.divHeight + 'px', 'overflow-y': 'auto' }}>
          {tooltips}
          {this.renderOverview()}
        </ModalBody>
        <ModalFooter>
          <Button color="secondary" onClick={this.toggleModal}>Close</Button>
        </ModalFooter>
      </Modal>
      </>
    )
  }
}

OverviewModal.propTypes = {
  graphState: PropTypes.object,
  handleNodeSelection: PropTypes.function,
  handleLinkSelection: PropTypes.function,
  divHeight: PropTypes.Number
}
