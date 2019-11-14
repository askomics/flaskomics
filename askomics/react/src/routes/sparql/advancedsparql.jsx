import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import { Collapse, CustomInput, Input, FormGroup, Label, Row, Col, Form, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'

export default class AdvancedSparql extends Component {
  constructor (props) {
    super(props)
    this.state = {
      isAdvancedOpen: false
    }
    this.toogleAdvanced = this.toogleAdvanced.bind(this)
  }


  toogleAdvanced () {
    this.setState(state => ({ isAdvancedOpen: !state.isAdvancedOpen }))
  }

  render () {

    return (
      <div>
        <div className="center-div">
          <Button color="link" onClick={this.toogleAdvanced}>Advanced options</Button>
        </div>
        <Collapse isOpen={this.state.isAdvancedOpen}>
          <br />


          <Row form>
            <Col md={6}>
              <h4>Local datasets</h4>
              <FormGroup check>
                {Object.keys(this.props.graphs).map((key, index) => {
                  return (<p key={this.props.graphs[key]["uri"]}><Input checked={this.props.graphs[key]["selected"]} value={this.props.graphs[key]["uri"]} onChange={this.props.handleChangeGraphs} type="checkbox" /> {this.props.graphs[key]["name"]}</p>)
                })}
              </FormGroup>
            </Col>
            <Col md={6}>
              <h4>Endpoints</h4>
              <FormGroup check>
                {Object.keys(this.props.endpoints).map((key, index) => {
                  return (<p key={this.props.endpoints[key]["uri"]}><Input checked={this.props.endpoints[key]["selected"]} value={this.props.endpoints[key]["uri"]} onChange={this.props.handleChangeEndpoints} type="checkbox" /> {this.props.endpoints[key]["name"]}</p>)
                })}
              </FormGroup>
            </Col>
          </Row>
        </Collapse>
      </div>
    )
  }
}

AdvancedSparql.propTypes = {
  graphs: PropTypes.object,
  endpoints: PropTypes.object,
  handleChangeGraphs: PropTypes.func,
  handleChangeEndpoints: PropTypes.func
}
