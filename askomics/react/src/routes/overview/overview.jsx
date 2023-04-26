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
import Switch from 'rc-switch';
import "rc-switch/assets/index.css";

export default class Overview extends Component {

  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      abstraction: [],
      is2D: true,
      graphState: {
        nodes: [],
        links: []
      },
      highlightNodes: new Set(),
      highlightLinks: new Set(),
      hoverNode: null
    }
    this.cancelRequest
    this.myRef = React.createRef();
    this.draw2DNode = this.draw2DNode.bind(this)
    this.onNodeHover = this.onNodeHover.bind(this)
    this.onLinkHover = this.onLinkHover.bind(this)
    this.getUniqueLinkId = this.getUniqueLinkId.bind(this)
    this.changeType = this.changeType.bind(this)
    this.zoom = this.zoom.bind(this)
    this.zoomOut = this.zoomOut.bind(this)
    this.focus = this.focus.bind(this)
    this.firstRender = true
  }

  changeType(checked){
    this.firstRender = true
    this.setState({
      is2D: checked
    })    
  }

  draw2DNode (node, ctx, globalScale){
    ctx.fillStyle = node.color
    ctx.lineWidth = 0.5
    if (node.id == this.state.hoverNode){
      ctx.strokeStyle = 'red'
      ctx.lineWidth = 2;
    } else if (this.state.highlightNodes.has(node.id)){
      ctx.strokeStyle = 'yellow'
      ctx.lineWidth = 2;
    } else {
      ctx.strokeStyle = '#808080'
    }

    ctx.globalAlpha = 1
    // draw node
    ctx.beginPath()
    ctx.arc(node.x, node.y, 3, 0, 2 * Math.PI, false)
    ctx.stroke()
    ctx.fill()
    ctx.closePath()
    // draw text
    ctx.beginPath()
    ctx.fillStyle = '#404040'
    ctx.font = '3px Sans-Serif'
    ctx.textAlign = 'middle'
    ctx.textBaseline = 'middle'
    let label = node.name
    ctx.fillText(label, node.x + 3, node.y + 3)
    ctx.closePath()
  }

  getNeighbors(nodeId){
    let links = []
    const neighbors = this.state.abstraction.relations.filter(link => (link.source == nodeId || link.target == nodeId)).map(link => {
      links.push(this.getUniqueLinkId(link, true))
      if(link.source == nodeId){
        return link.target
      } else if (link.target == nodeId) {
        return link.source
      }
    })
    return {neighbors, links}
  }

  getLinks3D(counts){
    let links = this.state.abstraction.relations.map(link => {
      let curvature = 0
      let rotation = 0
      let key = [link.source, link.target]
      let reverse_key = [link.target, link.source]
      let direction = counts[key].direction
      let current_key = counts[key].direction == 1 ? key : reverse_key

      if (link.source == link.target){
          curvature = counts[current_key].current * (1 / counts[current_key].count)
          rotation = 0

      } else if (counts[current_key].count !== 1) {
          curvature = 0.4
          rotation = direction * counts[current_key].current * (2* Math.PI / counts[current_key].count)
      }

      counts[current_key].current += 1
      return {source: link.source, target: link.target, name: link.label, curvature: curvature, rotation: rotation, uri: link.uri}
    })
    return links
  }


  getLinks2D(counts){
    let links = this.state.abstraction.relations.map(link => {
      let curvature = 0
      let rotation = 0
      let key = [link.source, link.target]
      let reverse_key = [link.target, link.source]
      let direction = counts[key].direction
      let current_key = counts[key].direction == 1 ? key : reverse_key
      let step
      let current

      if (link.source == link.target){
          curvature = direction * counts[current_key].current * (1 / counts[current_key].count)

      } else if (counts[current_key].count !== 1) {
          step = 2 / (counts[current_key].count - 1)
          current =  counts[current_key].current - 1
          curvature = direction + (-direction) * current * step
      }

      counts[current_key].current += 1
      return {source: link.source, target: link.target, name: link.label, curvature: curvature, rotation: rotation, uri: link.uri}
    })
    return links
  }

  initGraph() {
    let nodes = this.state.abstraction.entities.map(entity => {
      let { neighbors, links } = this.getNeighbors(entity.uri)
      return {id: entity.uri, name: entity.label, value: 1, color: this.utils.stringToHexColor(entity.uri), neighbors: neighbors, links: links}
    })

    let counts = {}

    this.state.abstraction.relations.map(link => {
      let direction = 1
      let currentCount = 1
      let key = [link.source, link.target]
      let reverse_key = [link.target, link.source]

      if (counts[key]){
        if (counts[key].direction == -1){
          counts[reverse_key].count += 1
        } else {
          counts[key].count += 1
        }
      } else {
        if (counts[reverse_key]){
          direction = -1
          counts[reverse_key].count += 1
        }
        counts[key] = {count: 1, current: 1, direction: direction}
      }

    })

    let links
    if (!this.state.is2D){
      links = this.getLinks3D(counts)
    } else {
      links = this.getLinks2D(counts)
    }

    this.setState({
      graphState: {nodes: nodes, links: links}
    })
  }

  onLinkHover(link){
    let highlightNodes = new Set();
    let highlightLinks = new Set();

    if (link) {
      highlightLinks.add(this.getUniqueLinkId(link));
      highlightNodes.add(link.source.id);
      highlightNodes.add(link.target.id);
    }

    this.setState({
      highlightNodes: highlightNodes,
      highlightLinks: highlightLinks
    })
  }

  onNodeHover(node) {
    let highlightNodes = new Set();
    let highlightLinks = new Set();
    let hoverNode = null

    if (node) {
      highlightNodes.add(node);
      node.neighbors.forEach(neighbor => highlightNodes.add(neighbor));
      node.links.forEach(link => highlightLinks.add(link));
      hoverNode = node.id
    }
    this.setState({
      highlightNodes: highlightNodes,
      highlightLinks: highlightLinks,
      hoverNode: hoverNode
    })
  }

  getUniqueLinkId (link, fromNode=false){
    if(fromNode){
      return link.uri + link.target + link.source
    }
    return link.uri + link.target.id + link.source.id
  }


  // ------------------------------------------------

  componentDidMount () {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/query/abstraction'
      axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
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
            this.firstRender = true
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

  zoom (){ 
    if(this.state.is2D){
      this.firstRender && this.myRef.current.zoomToFit(1000, 80)
    } 
    this.firstRender = false
  }

  zoomOut(){
    if (this.state.is2D){
      this.myRef.current.zoomToFit(1000, 80)
    } else {
      this.myRef.current.zoomToFit(1000, 0)
    }
  }

  focus (node){
    if (this.state.is2D){
      this.myRef.current.centerAt(node.x, node.y, 2000).zoom(5,2000)
    } else {
      const distance = 100;
      const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
      this.myRef.current.cameraPosition({ x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, node, 3000);
    }
  }

  render () {

    let graph
    const highlightNodes = new Set();
    const highlightLinks = new Set();
    let hoverNode = null;

    if (!this.state.is2D){
      graph = (
        <>
        <SizeMe>{({ size: { width } }) => (
          <ForceGraph3D
            graphData={this.state.graphState}
            ref={this.myRef}
            cooldownTicks={80}
            onEngineStop={() => this.zoom()}
            width={width}
            height={650}
            linkDirectionalArrowRelPos={1}
            linkDirectionalArrowLength={3.5}
            linkCurvature="curvature"
            linkCurveRotation="rotation"
            onNodeClick={this.focus}
            nodeThreeObject={node => {
              const sprite = new SpriteText(node.name);
              sprite.color = "white";
              sprite.position.y = 5.5;
              sprite.textHeight = 2;
              return sprite;
            }}
            nodeThreeObjectExtend={true}
            onNodeClick={this.focus}
          />       
        )}
        </SizeMe>
        </>
      )
    } else {
      graph = (
        <>
        <SizeMe>{({ size: { width } }) => (
          <ForceGraph2D
            ref={this.myRef}
            cooldownTicks={80}
            onEngineStop={() => this.zoom()}
            graphData={this.state.graphState}
            width={width}
            height={650}
            linkDirectionalArrowRelPos={1}
            linkDirectionalArrowLength={3.5}
            linkCurvature="curvature"
            linkCurveRotation="rotation"
            backgroundColor="Gainsboro"
            nodeCanvasObject={this.draw2DNode}
            onNodeHover={this.onNodeHover}
            onLinkHover={this.onLinkHover}
            onNodeClick={this.focus}
            linkWidth={link => this.state.highlightLinks.has(this.getUniqueLinkId(link)) ? 5 : 1}
            linkDirectionalParticles = {4}
            linkDirectionalParticleWidth = {link => this.state.highlightLinks.has(this.getUniqueLinkId(link)) ? 4 : 0}
          />
        )}
        </SizeMe>
        </>
      )
    }

    const options = [
     {
       label: "2D",
       value: "2D"
     },
     {
       label: "3D",
       value: "3D",
      }
    ];

    return (
      <div className="container">
        <h2>Abstraction visualization
        <div style={{float:"right"}}>
        <Switch
            onChange={this.changeType}
            checkedChildren="2D"
            unCheckedChildren="3D"
            defaultChecked={true}
            className="asko-switch-3d"
        /> 
        </div>
        </h2>
        <hr />
        Drag and scroll to interact with the graph. Click on a node to focus.
        <Button style={{float: "right"}} onClick={this.zoomOut}>Reset zoom</Button>     
        <br/>
        <WaitingDiv waiting={this.state.waiting} center />
        <br />
        {graph}
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage}/>
      </div>
    )
  }
}

Overview.propTypes = {
  waitForStart: PropTypes.bool,
  config: PropTypes.object
}
