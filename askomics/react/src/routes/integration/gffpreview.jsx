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
      attributesToIntegrate: Object.entries(props.file.data.attributes).map(([key, value]) => [key, new Set(value)]),
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

  handleAttributeSelection (event, entity) {

    let value = event.target.value
    let newAttr = {...this.state.attributesToIntegrate}

    if (!this.state.attributesToIntegrate[entity].has(value)) {
      newAttr[entity].add(value)
      this.setState({
        attributesToIntegrate: newAttr,
        publicTick: false,
        privateTick: false
      })
    }else {
      newAttr[entity].delete(value)
      this.setState({
        attributesToIntegrate: newAttr,
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
            <hr />
            <div>
              <h3>Select attributes to integrate for the selected entities</h3>
              <FormGroup check>
                {[...this.state.entitiesToIntegrate].map((entity) => {
                  let attr_div = this.state.availableAttributes[entity].map((attribute, indexA) => {
                    return (<p key={entity + attribute + "_" + index}><Input checked={this.state.attributesToIntegrate[entity].has(attribute)} value={attribute} onClick={(event) => this.handleAttributeSelection(event, entity)} type="checkbox" /> {attribute}</p>)
                  })
                  return (
                    <>
                    <h4>{entity}</h4>
                    {attr_div}
                    </>
                  )
                })}
              </FormGroup>
            </div>
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
