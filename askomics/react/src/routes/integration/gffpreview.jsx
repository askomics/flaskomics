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
      id: props.file.id,
      integrated: false,
      publicTick: false,
      privateTick: false,
      customUri: "",
      externalEndpoint: "",
      subEntities: {},
      errorMessage: null
    }

    let subEntities = {}
    Object.entries(this.state.availableAttributes).map(([key, values]) => {
        let data = new Set()
        values.map((value, valkey) => {
          data.add(value)
        })
        subEntities[key]= data
    })
    this.state.subEntities = subEntities
    this.cancelRequest
    this.integrate = this.integrate.bind(this)
    this.handleSubSelection = this.handleSubSelection.bind(this)
    this.handleSelection = this.handleSelection.bind(this)
  }

  integrate (event) {
    let requestUrl = '/api/files/integrate'
    let tick = event.target.value == 'public' ? 'publicTick' : 'privateTick'
    let selectedEntities = [...this.state.entitiesToIntegrate]
    let attributes = {}
    selectedEntities.map((key) => {
        attributes[key] = [...this.state.subEntities[key]]
    })

    let data = {
      fileId: this.state.id,
      entities: selectedEntities,
      attributes: attributes,
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
    } else {
      this.state.entitiesToIntegrate.delete(value)
      this.setState({
        entitiesToIntegrate: new Set([...this.state.entitiesToIntegrate]),
        publicTick: false,
        privateTick: false
      })
    }
  }


  handleSubSelection (event) {
    let value = event.target.value
    let name = event.target.name
    let state = this.state.subEntities
    if (!state[name].has(value)) {
      state[name].add(value)
      this.setState({subEntities:state})
    } else {
      state[name].delete(value)
      this.setState({subEntities:state})
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

  render () {

    let privateIcon = <i className="fas fa-lock"></i>
    if (this.state.privateTick) {
      privateIcon = <i className="fas fa-check text-success"></i>
    }
    let publicIcon = <i className="fas fa-globe-europe"></i>
    if (this.state.publicTick) {
      publicIcon = <i className="fas fa-check text-success"></i>
    }
    let publicButton
    if (this.props.config.user.admin) {
      publicButton = <Button onClick={this.integrate} value="public" color="secondary" disabled={this.state.publicTick}>{publicIcon} Integrate (public dataset)</Button>
    }

    let body
    if (this.props.file.error) {
      body = <ErrorDiv status={500} error={this.props.file.error} errorMessage={this.props.file.error_message} />
    } else {
      body = (
        <div>
          <br />
          <h4>Please select the entities to integrate:</h4>
          <br />
            <div>
              <FormGroup check>
                {Object.entries(this.state.availableAttributes).map(([key, values]) => {
                return (
                <div key={key}>
                <div>
                  <p><Input value={key} onClick={this.handleSelection} type="checkbox"/> {key}</p>
                  <FormGroup check inline hidden={this.state.entitiesToIntegrate.has(key)? false : true}>
                  Attributes of the entity:
                  {
                    values.map((value, valkey) => {
                      return (<div key={key + "_" + value}>&nbsp;<Input value={value} name={key} onClick={this.handleSubSelection} type="checkbox" defaultChecked={true} />{value}</div>)
                    })
                  }
                  </FormGroup>
                </div>
                <br />
                </div>
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
          customUri={this.state.customUri}
        />
        <br />
          <div className="center-div">
            <ButtonGroup>
              <Button onClick={this.integrate} value="private" color="secondary" disabled={this.state.privateTick}>{privateIcon} Integrate (private dataset)</Button>
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
