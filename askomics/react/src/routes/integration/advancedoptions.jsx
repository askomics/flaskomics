import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import { Collapse, CustomInput, Input, FormGroup, Label, Col, Form, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'

export default class AdvancedOptions extends Component {
  constructor (props) {
    super(props)
    this.state = {
      isAdvancedOpen: false
    }
    this.toogleAdvanced = this.toogleAdvanced.bind(this)
    this.handleChangeUri = this.props.handleChangeUri.bind(this)
    this.handleChangeEndpoint = this.props.handleChangeEndpoint.bind(this)
  }


  toogleAdvanced () {
    this.setState(state => ({ isAdvancedOpen: !state.isAdvancedOpen }))
  }

  render () {

    return (
      <div className="center-div">
        <Button color="link" onClick={this.toogleAdvanced}>Advanced options</Button>
        <Collapse isOpen={this.state.isAdvancedOpen}>
          <br />
          <Form>
            <FormGroup hidden={this.props.hideCustomUri} row>
              <Label for="uri" sm={2}>Custom URI</Label>
              <Col sm={8}>
                <Input onChange={this.handleChangeUri} value={this.props.customUri} type="text" name="uri" id="uri" placeholder={this.props.config.namespaceData} />
              </Col>
            </FormGroup>
            <FormGroup hidden={this.props.hideDistantEndpoint} row>
              <Label for="endpoint" sm={2}>Distant endpoint</Label>
              <Col sm={8}>
                <Input onChange={this.handleChangeEndpoint} value={this.props.externalEndpoint} type="text" name="endpoint" id="endpoint" placeholder="External endpoint" />
              </Col>
            </FormGroup>
          </Form>
        </Collapse>
      </div>
    )
  }
}

AdvancedOptions.propTypes = {
  config: PropTypes.object,
  handleChangeUri: PropTypes.function,
  handleChangeEndpoint: PropTypes.function,
  hideCustomUri: PropTypes.bool,
  customUri: PropTypes.string,
  hideDistantEndpoint: PropTypes.bool,
  externalEndpoint: PropTypes.string
}
