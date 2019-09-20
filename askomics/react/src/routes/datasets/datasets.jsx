import React, { Component } from 'react'
import axios from 'axios'
import DatasetsTable from './datasetstable'
import { Button } from 'reactstrap'
import PropTypes from 'prop-types'

export default class Datasets extends Component {
  constructor (props) {
    super(props)
    this.state = {
      error: false,
      errorMessage: null,
      waiting: true,
      datasets: [],
      selected: []
    }

    this.deleteSelectedDatasets = this.deleteSelectedDatasets.bind(this)
    this.cancelRequest
    this.interval
  }

  componentDidMount () {
    if (!this.props.waitForStart) {
      this.getDatasets()
      this.interval = setInterval(() => {
        this.getDatasets()
      }, 5000)
    }
  }

  componentWillUnmount () {
    clearInterval(this.interval)
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  getDatasets () {
    let requestUrl = '/api/datasets'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          datasets: response.data.datasets,
          waiting: false
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

  isDisabled () {
    return this.state.selected.length == 0
  }

  deleteSelectedDatasets () {
    let requestUrl = '/api/datasets/delete'
    let data = {
      datasetsIdToDelete: this.state.selected
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          datasets: response.data.datasets,
          selected: [],
          waiting: false
        })
      })
  }

  render () {
    return (
      <div>
        <div className="container">
          <h2>Datasets</h2>
          <hr />
          <DatasetsTable config={this.props.config} datasets={this.state.datasets} setStateDatasets={p => this.setState(p)} selected={this.state.selected} waiting={this.state.waiting} />
          <br />
          <Button disabled={this.isDisabled()} onClick={this.deleteSelectedDatasets} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
        </div>
      </div>
    )
  }
}

Datasets.propTypes = {
  config: PropTypes.object,
  waitForStart: PropTypes.bool
}
