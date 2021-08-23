import React, { Component } from 'react'
import axios from 'axios'
import { Row, Col, Input } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import Visualization from './visualization'
import PropTypes from 'prop-types'

export default class GraphFilters extends Component {
  constructor (props) {
    super(props)
  }

  render() {

    let filterNodeValue
    let filterLinkValue
    let disabled = false
    if (this.props.current != null) {
      if (this.props.current.type != "link") {
        this.props.graph.nodes.forEach(node => {
          if (node.id == this.props.current.id) {
            filterNodeValue = node.filterNode
            filterLinkValue = node.filterLink
          }
        })
      } else {
        disabled = true
        filterNodeValue = ""
        filterLinkValue = ""
      }
    } else {
      disabled = true
      filterNodeValue = ""
      filterLinkValue = ""
    }

    return (
      <Row>
        <Col md={6}>
          <div>
            <Input type="text" disabled={disabled} name="filterlinks" id="filterlinks" value={filterLinkValue} placeholder="Filter links" onChange={this.props.handleFilterLinks}/>
          </div>
        </Col>
        <Col md={6}>
          <div>
            <Input type="text" disabled={disabled} name="filternodes" id="filternodes" value={filterNodeValue} placeholder="Filter nodes" onChange={this.props.handleFilterNodes}/>
          </div>
        </Col>
      </Row>
    )
  }
}

GraphFilters.propTypes = {
  graph: PropTypes.object,
  current: PropTypes.object,
  showFaldo: PropTypes.bool,
  handleFilterLinks: PropTypes.func,
  handleFilterNodes: PropTypes.func,
  handleFilterFaldo: PropTypes.func
}
