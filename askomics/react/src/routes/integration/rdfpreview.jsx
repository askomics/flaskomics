import React, { Component } from 'react'
import axios from 'axios'
import { CustomInput, Input, FormGroup, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import AceEditor from 'react-ace'
import AdvancedOptions from './advancedoptions'
import ErrorDiv from '../error/error'

import "ace-builds/src-noconflict/mode-turtle";
// import "ace-builds/src-noconflict/mode-nt";
import "ace-builds/src-noconflict/mode-xml";
import "ace-builds/src-noconflict/theme-tomorrow";

export default class RdfPreview extends Component {
  constructor (props) {
    super(props)
    this.state = {
      name: props.file.name,
      preview: props.file.data.preview,
      id: props.file.id,
      integrated: false,
      publicTick: false,
      privateTick: false,
      customUri: "",
      externalEndpoint: props.file.data.location ? props.file.data.location : "",
      error: false,
      errorMessage: null,
      status: null
    }
    this.cancelRequest
    this.integrate = this.integrate.bind(this)
    this.handleCodeChange = this.handleCodeChange.bind(this)
  }

  handleCodeChange (event) {
    // FIXME: we use this to prevent editing
    this.setState({
        preview: this.state.preview
    })

  }

  integrate (event) {
    let requestUrl = '/api/files/integrate'
    let tick = event.target.value == 'public' ? 'publicTick' : 'privateTick'
    let data = {
      fileId: this.state.id,
      public: event.target.value == 'public',
      type: this.props.file.type,
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

  guess_mode(type) {
    if (type == "rdf/ttl") {
      return "turtle"
    }
    if (type == "rdf/xml") {
      return "xml"
    }
    if (type == "rdf/nt") {
      return "text"
    }
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

    return (
      <div>
        <h4>{this.state.name} (preview)</h4>
        <br />
        <div className="center-div">
            <div>
              <AceEditor
                mode={this.guess_mode(this.props.file.type)}
                theme="tomorrow"
                name="ttl_preview"
                fontSize={14}
                showPrintMargin={true}
                showGutter={true}
                highlightActiveLine={false}
                value={this.props.file.data.preview}
                height={300}
                width={'auto'}
                onChange={this.handleCodeChange}
              />
            </div>
          <br />
        <AdvancedOptions
          hideCustomUri={true}
          config={this.props.config}
          handleChangeEndpoint={p => this.handleChangeEndpoint(p)}
          externalEndpoint={this.state.externalEndpoint}
          handleChangeUri={p => this.handleChangeUri(p)}
        />
        <br />
        <div className="center-div">
          <ButtonGroup>
            {privateButton}
            {publicButton}
          </ButtonGroup>
        </div>
        </div>
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

RdfPreview.propTypes = {
  file: PropTypes.object,
  config: PropTypes.object
}
