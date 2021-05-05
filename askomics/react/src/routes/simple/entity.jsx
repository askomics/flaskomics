import React, { Component} from 'react'
import axios from 'axios'
import { Input, FormGroup, CustomInput, FormFeedback } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import DatePicker from "react-datepicker";
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import Visualization from './visualization'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'

export default class Entity extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {}
  }


  render () {
    let entity = this.props.entity
    let attribute_boxes = this.props.attribute_boxes
    return(
      <div>
        <h3>{entity}</h3>
        {attribute_boxes}
      </div>
    )
  }
}

Entity.propTypes = {
  attribute_boxes: PropTypes.list,
  entity: PropTypes.string,
}
