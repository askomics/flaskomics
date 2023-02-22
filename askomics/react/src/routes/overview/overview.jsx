import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button, CustomInput, Row, Col, ButtonGroup, Input, Spinner, ButtonToolbar } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import Utils from '../../classes/utils'
import { ForceGraph2D, ForceGraph3D } from 'react-force-graph';

export default class Overview extends Component {

  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      config: this.props.location.state.config,
      abstraction: [],
      graphState: {
        nodes: [],
        edges: []
      },
    }
  }


  initGraph() {
    let nodes = this.state.abstraction.entities.map(entity => {
      return {id: entity.uri, name: entity.label, value: 1, color: this.Utils.stringToHexColor(entity.uri)}
    })

    let edges = this.state.abstraction.relations.map(link =>{
      return {source: link.source, link.target}
    })

    this.setState({
      graphState: {nodes: nodes, edges: edges}
    })
  }


  // ------------------------------------------------

  componentDidMount () {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/query/abstraction'
      axios.get(requestUrl, { baseURL: this.state.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
          console.log(requestUrl, response.data)
          this.setState({
            waiting: false,
            abstraction: response.data.abstraction,
          })
        })
        .catch(error => {
          console.log(error, error.response.data.errorMessage)
          this.setState({
            error: true,
            errorMessage: error.response.data.errorMessage,
            status: error.response.status
          })
        }).then(response => {
            this.initGraph()
            this.setState({ waiting: false })
        })
    }
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  render () {
    let visualizationDiv
    if (!this.state.waiting) {
      // visualization (left view)
      visualizationDiv = (
        <ForceGraph3D graphData={this.state.graphState}/>
      )
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>Abstraction visualization</h2>
        <hr />
        <WaitingDiv waiting={this.state.waiting} center />
        <br />
        {visualizationDiv}
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} customMessages={{"504": "Query time is too long, use Run & Save to get your results", "502": "Query time is too long, use Run & Save to get your results"}} />
      </div>
    )
  }
}

Overview.propTypes = {
  location: PropTypes.object,
  waitForStart: PropTypes.bool
}
