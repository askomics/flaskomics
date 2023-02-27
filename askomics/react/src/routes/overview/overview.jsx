import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button, CustomInput, Row, Col, ButtonGroup, Input, Spinner, ButtonToolbar } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import Utils from '../../classes/utils'
import PropTypes from 'prop-types'
import { ForceGraph2D, ForceGraph3D } from 'react-force-graph';
import { SizeMe } from 'react-sizeme';
import SpriteText from 'three-spritetext';


export default class Overview extends Component {

  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      abstraction: [],
      graphState: {
        nodes: [],
        links: []
      },
    }
    this.cancelRequest
  }

  initGraph() {
    let nodes = this.state.abstraction.entities.map(entity => {
      return {id: entity.uri, name: entity.label, value: 1, color: this.utils.stringToHexColor(entity.uri)}
    })

    let links = this.state.abstraction.relations.map(link => {
      if (link.source == link.target){console.log(link)}
      return {source: link.source, target: link.target, name: link.label}
    })

    this.setState({
      graphState: {nodes: nodes, links: links}
    })
  }


  // ------------------------------------------------

  componentDidMount () {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/query/abstraction'
      axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
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
    return (
      <div className="container">
        <h2>Abstraction visualization</h2>
        <hr />
        <WaitingDiv waiting={this.state.waiting} center />
        <br />
        <SizeMe>{({ size: { width } }) => (
        <ForceGraph3D 
            graphData={this.state.graphState} 
            width={width} 
            height={650} 
            linkDirectionalArrowRelPos={1}
            linkDirectionalArrowLength={3.5}
            nodeThreeObject={node => {
              const sprite = new SpriteText(node.name);
              sprite.color = node.color;
              sprite.textHeight = 4;
              return sprite;
            }}
            nodeThreeObjectExtend={true}            
            linkThreeObjectExtend={true}
            linkThreeObject={link => {
              // extend link with text sprite
              const sprite = new SpriteText(link.name);
              sprite.color = 'lightgrey';
              sprite.textHeight = 1.5;
              return sprite;
            }}
            linkPositionUpdate={(sprite, { start, end }) => {
              const middlePos = Object.assign(...['x', 'y', 'z'].map(c => ({
                [c]: start[c] + (end[c] - start[c]) /2 // calc middle point
              })));
              // Position sprite
              Object.assign(sprite.position, middlePos);
            }}
        />
        

        )}
        </SizeMe>
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage}/>
      </div>
    )
  }
}

Overview.propTypes = {
  waitForStart: PropTypes.bool,
  config: PropTypes.object
}
