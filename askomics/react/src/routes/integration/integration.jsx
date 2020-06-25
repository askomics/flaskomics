import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Input, Button, ButtonGroup } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import CsvTable from './csvtable'
import RdfPreview from './rdfpreview'
import GffPreview from './gffpreview'
import BedPreview from './bedpreview'
import PropTypes from 'prop-types'

export default class Integration extends Component {
  constructor (props) {
    super(props)
    this.state = {
      waiting: true,
      error: false,
      errorMessage: null,
      config: this.props.location.state.config,
      filesId: this.props.location.state.filesId,
      previewFiles: []
    }
    this.cancelRequest
  }

  componentDidMount () {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/files/preview'
      let data = {
        filesId: this.state.filesId
      }
      axios.post(requestUrl, data, { baseURL: this.state.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
          console.log(requestUrl, response.data)
          this.setState({
            previewFiles: response.data.previewFiles,
            waiting: false,
            error: response.data.error,
            errorMessage: response.data.errorMessage
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
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  render () {
    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>Integrate</h2>
        <hr />

        {
          this.state.previewFiles.map(file => {
            console.log(file)
            if (file.type == 'csv/tsv') {
              return <CsvTable config={this.state.config} key={file.name} file={file} />
            }
            if (["rdf/ttl", "rdf/xml", "rdf/nt"].includes(file.type)) {
              return <RdfPreview config={this.state.config} file={file} />
            }
            if (file.type == 'gff/gff3') {
              return <GffPreview config={this.state.config} file={file} />
            }
            if (file.type == 'bed') {
              return <BedPreview config={this.state.config} file={file} />
            }
          })
        }

        <WaitingDiv waiting={this.state.waiting} center="center" />
        <br />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

Integration.propTypes = {
  location: PropTypes.object,
  waitForStart: PropTypes.bool
}
