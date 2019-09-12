import React, { Component } from 'react'
import axios from 'axios'
import { CustomInput, Input, FormGroup, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import AskoContext from '../../components/context'

export default class GffPreview extends Component {
  static contextType = AskoContext
  constructor (props) {
    super(props)
    this.state = {
      name: props.file.name,
      availableEntities: props.file.data.entities,
      entitiesToIntegrate: new Set(),
      id: props.file.id,
      integrated: false,
      publicTick: false,
      privateTick: false
    }
    this.cancelRequest
    this.integrate = this.integrate.bind(this)
    this.handleSelection = this.handleSelection.bind(this)
  }

  integrate (event) {
    let requestUrl = '/api/files/integrate'
    let tick = event.target.value == 'public' ? 'publicTick' : 'privateTick'
    let data = {
      fileId: this.state.id,
      entities: [...this.state.entitiesToIntegrate],
      public: event.target.value == 'public',
      type: 'gff/gff3'
    }
    axios.post(requestUrl, data, { baseURL: this.context.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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

  render () {

    let privateIcon = <i className="fas fa-lock"></i>
    if (this.state.privateTick) {
      privateIcon = <i className="fas fa-check text-success"></i>
    }
    let publicIcon = <i className="fas fa-globe-europe"></i>
    if (this.state.publicTick) {
      publicIcon = <i className="fas fa-check text-success"></i>
    }

    return (
      <div>
        <h4>{this.state.name} (preview)</h4>
        <br />
            <div>
              <FormGroup check>
                {this.state.availableEntities.map((entity, index) => {
                  return (<p key={entity + "_" + index}><Input value={entity} onClick={this.handleSelection} type="checkbox" /> {entity}</p>)
                })}
              </FormGroup>
            </div>
          <br />
          <ButtonGroup>
            <Button onClick={this.integrate} value="private" color="secondary" disabled={this.state.privateTick}>{privateIcon} Integrate (private dataset)</Button>
            <Button onClick={this.integrate} value="public" color="secondary" disabled={this.state.publicTick}>{publicIcon} Integrate (public dataset)</Button>
          </ButtonGroup>
      </div>
    )
  }
}

GffPreview.propTypes = {
  file: PropTypes.object
}
