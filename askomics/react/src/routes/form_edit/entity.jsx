import React, { Component} from 'react'
import axios from 'axios'
import { Input, FormGroup, CustomInput, FormFeedback, Label } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import DatePicker from "react-datepicker";
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'

export default class Entity extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {}
  }


  render () {
    let entity_id = this.props.entity_id
    let entity = this.props.entity
    let attribute_boxes = this.props.attribute_boxes
    return(
      <div>
      <FormGroup>
          <Label for="fname">Entity name</Label>
          <Input type="text" id={entity_id} placeholder={entity} value={this.props.entity} onChange={this.props.setEntityName} />
        </FormGroup>
        {attribute_boxes}
      </div>
    )
  }
}

Entity.propTypes = {
  setEntityName: PropTypes.func,
  attribute_boxes: PropTypes.list,
  entity: PropTypes.string,
  entity_id: PropTypes.number,
}
