import React, { Component } from 'react'
import axios from 'axios'
import { CustomInput, Input, FormGroup, Label, ButtonGroup, Button, Col } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import AdvancedOptions from './advancedoptions'
import ErrorDiv from '../error/error'

export default class BedPreview extends Component {
  constructor (props) {
    super(props)
    console.log("entity_name", props.file.entity_name)
    this.state = {
      name: props.file.name,
      entityName: props.file.entity_name,
      id: props.file.id,
      integrated: false,
      publicTick: false,
      privateTick: false,
      customUri: "",
      externalEndpoint: "",
      error: false,
      errorMessage: null,
      status: null,
      externalGraph: ""
    }
    this.cancelRequest
    this.integrate = this.integrate.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }

  handleChange (event) {
    this.setState({
      entityName: event.target.value,
      publicTick: false,
      privateTick: false
    })
  }

  integrate (event) {
    let requestUrl = '/api/files/integrate'
    let tick = event.target.value == 'public' ? 'publicTick' : 'privateTick'
    let data = {
      fileId: this.state.id,
      entity_name: this.state.entityName,
      public: event.target.value == 'public',
      type: 'bed',
      customUri: this.state.customUri,
      externalEndpoint: this.state.externalEndpoint
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          [tick]: true
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          waiting: false
        })
      })
  }

  handleChangeUri (event) {
    this.setState({
      customUri: event.target.value,
      publicTick: false,
      privateTick: false
    })
  }

  handleChangeEndpoint (event) {
    this.setState({
      externalEndpoint: event.target.value,
      publicTick: false,
      privateTick: false
    })
  }

  render () {

    let privateIcon = <i className="fas fa-lock"></i>
    if (this.state.privateTick) {
      privateIcon = <i className="fas fa-check text-success"></i>
    }
    let publicIcon = <i className="fas fa-globe-europe"></i>
    if (this.state.publicTick) {
      publicIcon = <i className="fas fa-check text-success"></i>
    }
    let privateButton
    if (this.props.config.user.admin || !this.props.config.singleTenant){
        privateButton = <Button onClick={this.integrate} value="private" color="secondary" disabled={this.state.privateTick}>{privateIcon} Integrate (private dataset)</Button>
    }
    let publicButton
    if (this.props.config.user.admin || this.props.config.singleTenant) {
      publicButton = <Button onClick={this.integrate} value="public" color="secondary" disabled={this.state.publicTick}>{publicIcon} Integrate (public dataset)</Button>
    }

    let body

    if (this.props.file.error) {
      body = (
        <ErrorDiv status={500} error={this.props.file.error} errorMessage={this.props.file.error_message} />
      )
    } else {
      body = (
        <div>
          <br />

          <FormGroup md={4}>
            <Label for="entityName">Entity name</Label>
            <Input type="text" name="entityName" id="entityName" placeholder="Entity name" value={this.state.entityName} onChange={this.handleChange} />
          </FormGroup>

          <br />
          <AdvancedOptions
            config={this.props.config}
            hideDistantEndpoint={true}
            handleChangeUri={p => this.handleChangeUri(p)}
            handleChangeEndpoint={p => this.handleChangeEndpoint(p)}
            handleChangeExternalGraph={p => this.handleChangeExternalGraph(p)}
            externalGraph={this.state.externalGraph}
            customUri={this.state.customUri}
          />
          <br />
          <div className="center-div">
            <ButtonGroup>
              {privateButton}
              {publicButton}
            </ButtonGroup>
            <br />
            <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
          </div>
        </div>
      )
    }

    return (
      <div>
        <h4>{this.state.name} (preview)</h4>
        {body}
      </div>
    )
  }
}

BedPreview.propTypes = {
  file: PropTypes.object,
  config: PropTypes.object
}
