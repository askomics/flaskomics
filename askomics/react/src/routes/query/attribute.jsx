import React, { Component } from "react"
import axios from 'axios'
import { Alert, Button, Row, Col, Input } from 'reactstrap';
import { Redirect} from 'react-router-dom'
import ErrorDiv from "../error/error"
import WaitingDiv from "../../components/waiting"
import update from 'react-addons-update'
import Visualization from './visualization'

export default class AttributeBox extends Component {

  constructor(props) {
    super(props)
    this.state = {

    }
  }


  renderText() {
    return(
      <div className="attribute-box">
        <label className="attr-label">{this.props.label}</label>
        <div className="attr-icons">
          <i className="fas fa-eye"></i>
        </div>
        <Input type="text" name="name" id="id" />
      </div>
    )
  }

  renderNumeric() {
    return(
      <div className="attribute-box">
        <label className="attr-label">{this.props.label}</label>
        <div className="attr-icons">
          <i className="fas fa-eye"></i>
        </div>
        <Input type="text" name="name" id="id" />
      </div>
    )
  }

  renderCategory() {
    return(
      <div className="attribute-box">
        <label className="attr-label">{this.props.label}</label>
        <div className="attr-icons">
          <i className="fas fa-eye"></i>
        </div>
        <Input type="text" name="name" id="id" />
      </div>
    )
  }


  render() {
    let box
    if (this.props.type == "text") {
      box = this.renderText()
    }
    if (this.props.type == "numeric") {
      box = this.renderNumeric()
    }
    if (this.props.type == "category") {
      box = this.renderCategory()
    }
    return box
  }
}