import React, { Component } from 'react'
import axios from 'axios'
import { CustomInput, Input, FormGroup, Label, ButtonGroup, Button, Col } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import AskoContext from '../../components/context'

export default class BedPreview extends Component {
  static contextType = AskoContext
  constructor (props) {
    super(props)
    console.log("entity_name", props.file.entity_name)
    this.state = {
      name: props.file.name,
      entityName: props.file.entity_name,
      id: props.file.id,
      integrated: false,
      publicTick: false,
      privateTick: false
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
      type: 'bed'
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
    if (this.props.user.admin) {
      publicButton = <Button onClick={this.integrate} value="public" color="secondary" disabled={this.state.publicTick}>{publicIcon} Integrate (public dataset)</Button>
    }

    return (
      <div>
        <h4>{this.state.name} (preview)</h4>
        <br />

        <FormGroup md={4}>
          <Label for="entityName">Entity name</Label>
          <Input type="text" name="entityName" id="entityName" placeholder="Entity name" value={this.state.entityName} onChange={this.handleChange} />
        </FormGroup>

        <br />
        <ButtonGroup>
          <Button onClick={this.integrate} value="private" color="secondary" disabled={this.state.privateTick}>{privateIcon} Integrate (private dataset)</Button>
          {publicButton}
        </ButtonGroup>
      </div>
    )
  }
}

BedPreview.propTypes = {
  file: PropTypes.object
}
