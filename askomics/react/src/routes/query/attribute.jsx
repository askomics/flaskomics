import React, { Component } from "react"
import axios from 'axios'
import { Input, FormGroup, CustomInput } from 'reactstrap';
import { Redirect} from 'react-router-dom'
import ErrorDiv from "../error/error"
import WaitingDiv from "../../components/waiting"
import update from 'react-addons-update'
import Visualization from './visualization'

export default class AttributeBox extends Component {

  constructor(props) {
    super(props)
    this.state = {}

    this.toggleVisibility = this.props.toggleVisibility.bind(this)
    this.toggleFilterType = this.props.toggleFilterType.bind(this)
    this.handleFilterValue = this.props.handleFilterValue.bind(this)
    this.handleFilterCategory = this.props.handleFilterCategory.bind(this)
  }


  renderText() {
    let eyeIcon = "attr-icon fas fa-eye-slash"
    if (this.props.attribute.visible) {
      eyeIcon = "attr-icon fas fa-eye"
    }
    let filterIcon = "attr-icon fas fa-filter"
    if (this.props.attribute.filterType == "exact") {
      filterIcon = "attr-icon fas fa-font"
    }

    return(
      <div className="attribute-box">
        <label className="attr-label">{this.props.attribute.label}</label>
        <div className="attr-icons">
          <i className={filterIcon} id={this.props.attribute.id} onClick={this.toggleFilterType}></i>
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility}></i>
        </div>
        <Input type="text" name="name" id={this.props.attribute.id} value={this.props.attribute.filterValue} onChange={this.handleFilterValue} />
      </div>
    )
  }

  renderNumeric() {
    return(
      <div className="attribute-box">
        <label className="attr-label">{this.props.attribute.label}</label>
        <div className="attr-icons">
          <i className="fas fa-eye"></i>
        </div>
        <Input type="text" name="name" id="id" />
      </div>
    )
  }


  renderCategory() {
    let eyeIcon = "attr-icon fas fa-eye-slash"
    if (this.props.attribute.visible) {
      eyeIcon = "attr-icon fas fa-eye"
    }

    let categoryFormGroup = (
      <FormGroup>
        <CustomInput style={{height: "60px"}} className="attr-select" type="select" id={this.props.attribute.id} onChange={this.handleFilterCategory} multiple>
        {this.props.attribute.filterValues.map(value => {
          let selected = this.props.attribute.filterSelectedValues.includes(value.uri)
          return (<option attrId={this.props.attribute.uri} value={value.uri} selected={selected}>{value.label}</option>)
        })}
        </CustomInput>
      </FormGroup>
    )

    return(
      <div className="attribute-box">
        <label className="attr-label">{this.props.attribute.label}</label>
        <div className="attr-icons">
          <i className={eyeIcon} id={this.props.attribute.id} onClick={this.toggleVisibility}></i>
        </div>
        {categoryFormGroup}
      </div>
    )
  }


  render() {
    let box = null
    if (this.props.attribute.type == "text") {
      box = this.renderText()
    }
    if (this.props.attribute.type == "numeric") {
      box = this.renderNumeric()
    }
    if (this.props.attribute.type == "category") {
      box = this.renderCategory()
    }
    return box
  }
}