import React, { Component } from 'react'
import axios from 'axios'
import { CustomInput, Input, FormGroup, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import AdvancedOptions from './advancedoptions'
import ErrorDiv from '../error/error'

export default class GffPreview extends Component {
  constructor (props) {
    super(props)
    this.state = {
      name: props.file.name,
      availableEntities: props.file.data.entities,
      availableAttributes: props.file.data.attributes,
      entitiesToIntegrate: new Set(),
      attributesToIntegrate: new Set(),
      id: props.file.id,
      integrated: false,
      publicTick: false,
      privateTick: false,
      customUri: "",
      externalEndpoint: "",
      externalGraph: ""
    }
    this.cancelRequest
    this.integrate = this.integrate.bind(this)
    this.handleSelection = this.handleSelection.bind(this)
    this.handleAttributeSelection = this.handleAttributeSelection.bind(this)
  }

  integrate (event) {
    let requestUrl = '/api/files/integrate'
    let tick = event.target.value == 'public' ? 'publicTick' : 'privateTick'
    let data = {
      fileId: this.state.id,
      entities: [...this.state.entitiesToIntegrate],
      attributes: [...this.state.attributesToIntegrate],
      public: event.target.value == 'public',
      type: 'gff/gff3',
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

  handleSelection (event) {

    let value = event.target.value

    if (!this.state.entitiesToIntegrate.has(value)) {
      this.setState({
        entitiesToIntegrate: new Set([...this.state.entitiesToIntegrate]).add(value),
        publicTick: false,
        privateTick: false
      })
    }else {
      this.state.entitiesToIntegrate.delete(value)
      this.setState({
        entitiesToIntegrate: new Set([...this.state.entitiesToIntegrate]),
        publicTick: false,
        privateTick: false
      })
    }
  }

  handleAttributeSelection (event) {

    let value = event.target.value

    if (!this.state.attributesToIntegrate.has(value)) {
      this.setState({
        attributesToIntegrate: new Set([...this.state.attributesToIntegrate]).add(value),
        publicTick: false,
        privateTick: false
      })
    }else {
      this.state.attributesToIntegrate.delete(value)
      this.setState({
        attributesToIntegrate: new Set([...this.state.attributesToIntegrate]),
        publicTick: false,
        privateTick: false
      })
    }
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

  handleChangeRemoteGraph (event) {
    this.setState({
      remoteGraph: event.target.value,
      publicTick: false,
      privateTick: false
    })
  }

  handleChangeExternalGraph (event) {
    this.setState({
      externalGraph: event.target.value,
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
      body = <ErrorDiv status={500} error={this.props.file.error} errorMessage={this.props.file.error_message} />
    } else {
      body = (
        <div>
          <br />
            <div>
              <h3>Select entities to integrate</h3>
              <FormGroup check>
                {this.state.availableEntities.map((entity, index) => {
                  return (<p key={entity + "_" + index}><Input value={entity} onClick={this.handleSelection} type="checkbox" /> {entity}</p>)
                })}
              </FormGroup>
            </div>
            <hr>
            <FormGroup check>
              {this.state.availableAttributes &&
                <h3>Select attributes to integrate</h3>
              }
              {this.state.availableAttributes.map((attribute, index) => {
                return (<p key={attribute + "_" + index}><Input value={attribute} onClick={this.handleAttributeSelection} type="checkbox" /> {attribute}</p>)
              })}
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

GffPreview.propTypes = {
  file: PropTypes.object,
  config: PropTypes.object
}
