import React, { Component} from 'react'
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, ButtonGroup, Input } from 'reactstrap'
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
  }

  toggleModal () {
    this.setState({
      modal: !this.state.modal
    })
  }

  renderLinker (attribute) {
    const linked = this.props.graphState.attributes.find(attr => attr.id == attribute.linkedWith);
    return (
        <CustomInput disabled value={linked.displayLabel}/>
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

    let selected_sign = attribute.negative ? "≠" : '='

    return form = (
      <table style={{ width: '100%' }}>
        <tr>
          <td>
            <CustomInput disabled value={attribute.filterType}/>
          </td>
          <td>
            <CustomInput disabled value={selected_sign}/>
          </td>
          <td>
            <CustomInput disabled value={attribute.filterValue}/>
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

    return form = (
      <FormGroup>
        <CustomInput disabled style={{ height: '60px' }} className="attr-select" type="select" multiple>
          {attribute.filterValues.filter(val => attribute.filterSelectedValues.includes(val.uri)).map(value => {
            return (<option key={value.uri} selected>{value.label}</option>)
          })}
        </CustomInput>
      </FormGroup>
    )
  }

  renderNumField(attribute){
    if (attribute.linked && attribute.linkedWith){
      return this.renderLinker(attribute)
    }

    if (attribute.filters.length == 0){
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

    return form = (
      <table style={{ width: '100%' }}>
      {attribute.filters.map((filter, index) => {
        return (
          <tr key={index}>
            <td key={index}>
              <CustomInput key={index} data-index={index} disabled type="select" id={attribute.id}}>
                  <option selected>{sign_display[filter.filterSign]}</option>
              </CustomInput>
            </td>
              <td>
              <CustomInput disabled value={filter.filterValue}/>
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
      form = this.renderText()
    }
    if (attribute.type == 'decimal' || attribute.type == 'date') {
      box = this.renderNumeric()
    }
    if (attribute.type == 'category' || attribute.type == 'boolean') {
      box = this.renderCategory()
    }

    if (!(form && icons)){
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
    // Iterate on attribute, store it as nodeiD = list of attr to string
    // Need to store "Options" and "Filters"
    // Then get the related Nodes names
    let data = this.props.graphState.attributes.map(attr => this.attrOverview(attr)).filter(attr => attr);
    return data
  }

  render () {
    return(
      <div>
        <Modal isOpen={this.state.modal} toggle={this.toggleModal}>
          <ModalHeader toggle={this.toggleModal}>Query overview</ModalHeader>
          <ModalBody>
            {this.renderOverview()}
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModal}>Close</Button>
          </ModalFooter>
        </Modal>
      </div>
    )
  }
}

OverviewModal.propTypes = {
  graphState: PropTypes.object
}
