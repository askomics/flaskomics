import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import { CustomInput, Input, FormGroup, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'

export default class TtlPreview extends Component {
  constructor (props) {
    super(props)
    this.state = {
      name: props.file.name,
      id: props.file.id,
      integrated: false,
      publicTick: false,
      privateTick: false
    }
    this.cancelRequest
    this.integrate = this.integrate.bind(this)
  }

  integrate (event) {
    let requestUrl = '/api/files/integrate'
    let tick = event.target.value == 'public' ? 'publicTick' : 'privateTick'
    let data = {
      fileId: this.state.id,
      public: event.target.value == 'public',
      type: 'turtle'
    }
    axios.post(requestUrl, data, { cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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

    return (
      <div>
        <h4>{this.state.name} (preview)</h4>
        <br /><br />
        <div className="center-div">
          <ButtonGroup>
            <Button onClick={this.integrate} value="private" color="secondary" disabled={this.state.privateTick}>{privateIcon} Integrate (private dataset)</Button>
            <Button onClick={this.integrate} value="public" color="secondary" disabled={this.state.publicTick}>{publicIcon} Integrate (public dataset)</Button>
          </ButtonGroup>
        </div>
      </div>
    )
  }
}

TtlPreview.propTypes = {
  file: PropTypes.object
}
