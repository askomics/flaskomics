import React, { Component } from "react"
// import ReactDOM from 'react-dom'
import axios from 'axios'
import { Alert, Button } from 'reactstrap';
import { Redirect} from 'react-router-dom'
import ErrorDiv from "../error/error"
import WaitingDiv from "../../components/waiting"
import update from 'react-addons-update'
import * as d3 from "d3"
import { ForceGraph2D } from 'react-force-graph';

export default class Visualization extends Component {

  constructor(props) {
    super(props)
    this.state = {
      error: false,
      errorMessage: null
    }

    // graph constants
    this.w = 500
    this.h = 500
    this.colorGrey = "#808080"
    this.colorDarkGrey = "#404040"
    this.colorFirebrick = "#cc0000"
    this.lineWidth = 0.5
    this.nodeSize = 3
    this.arrowLength = 7

    this.cancelRequest
    this.handleSelection = this.props.handleSelection.bind(this)
    this.drawNode = this.drawNode.bind(this)
    this.drawLink = this.drawLink.bind(this)
  }

  stringToHexColor(str) {
    // first, hash the string into an int
    let hash = 0
    for (var i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash)
    }
    // Then convert this int into a rgb color code
    let c = (hash & 0x00FFFFFF).toString(16).toUpperCase()
    let hex = "#" + "00000".substring(0, 6 - c.length) + c
    return hex
  }

  IntersectionCoordinate(x1, y1, x2, y2, r) {
    let theta = Math.atan((y2 - y1) / (x1 - x2))
    let x
    let y
    if (x1 < x2) {
      x = x1 + r * Math.cos(theta)
      y = y1 - r * Math.sin(theta)
    } else {
      x = x1 - r * Math.cos(theta)
      y = y1 + r * Math.sin(theta)
    }
    return {x: x, y: y}
  }

  middleCoordinate(x1, y1, x2, y2) {
    let theta = Math.atan((y2 - y1) / (x1 - x2))
    let x
    let y
    if (x1 < x2) {
      x = x1 + 12 * Math.cos(theta)
      y = y1 - 12 * Math.sin(theta)
    } else {
      x = x1 - 12 * Math.cos(theta)
      y = y1 + 12 * Math.sin(theta)
    }
    return {x: x, y: y}
  }

  triangleCoordinate(x1, y1, x2, y2, headlen) {
    let theta = Math.atan2(y1 - y2, x1 - x2)

    let xa = x1 - headlen * Math.cos(theta - Math.PI / 14)
    let ya = y1 - headlen * Math.sin(theta - Math.PI / 14)

    let xb = x1 - headlen * Math.cos(theta + Math.PI / 14)
    let yb = y1 - headlen * Math.sin(theta + Math.PI / 14)

    return {
      xa: xa,
      ya: ya,
      xb: xb,
      yb: yb
    }
  }

  drawNode(node, ctx, globalScale) {
    // node style
    ctx.fillStyle = this.stringToHexColor(node.uri)
    ctx.lineWidth = this.lineWidth
    ctx.beginPath()
    ctx.arc(node.x, node.y, this.nodeSize, 0, 2 * Math.PI, false)
    // stroke style
    ctx.strokeStyle = node.selected ? this.colorFirebrick : this.colorGrey
    ctx.globalAlpha = node.suggested ? 0.5 : 1
    node.suggested ? ctx.setLineDash([this.lineWidth, this.lineWidth]) : ctx.setLineDash([])
    ctx.stroke()
    ctx.fill()
    ctx.closePath()
    // text
    ctx.beginPath()
    ctx.fillStyle = this.colorDarkGrey
    ctx.font = this.nodeSize + 'px Sans-Serif'
    ctx.textAlign = 'middle'
    ctx.textBaseline = 'middle'
    ctx.fillText(node.label, node.x + this.nodeSize, node.y + this.nodeSize)
    ctx.closePath()
  }

  drawLink(link, ctx, globalScale) {
    link.suggested ? ctx.setLineDash([this.lineWidth, this.lineWidth]) : ctx.setLineDash([])
    ctx.strokeStyle = this.colorGrey
    ctx.fillStyle = this.colorGrey
    ctx.globalAlpha = link.suggested ? 0.3 : 1
    ctx.lineWidth = this.lineWidth
    ctx.beginPath()
    // first point (source)
    let c = this.IntersectionCoordinate(link.source.x, link.source.y, link.target.x, link.target.y, this.nodeSize)
    ctx.moveTo(c.x, c.y)
    // second point (target)
    c = this.IntersectionCoordinate(link.target.x, link.target.y, link.source.x, link.source.y, this.nodeSize)
    ctx.lineTo(c.x, c.y)
    ctx.stroke()
    ctx.closePath()
    // arrow
    ctx.beginPath()
    let triangle = this.triangleCoordinate(link.target.x, link.target.y, link.source.x, link.source.y, this.arrowLength)
    ctx.moveTo(c.x, c.y)
    ctx.lineTo(triangle.xa, triangle.ya)
    ctx.lineTo(triangle.xb, triangle.yb)
    ctx.fill()
    ctx.closePath()

    // text
    ctx.beginPath()
    ctx.fillStyle = this.colorDarkGrey
    ctx.font = this.nodeSize - 0.5 + 'px Sans-Serif'
    ctx.textAlign = 'middle'
    ctx.textBaseline = 'middle'
    let m = this.middleCoordinate(link.source.x, link.source.y, link.target.x, link.target.y)
    ctx.fillText(link.label, m.x, m.y)
    ctx.closePath()


    // build link
    // ctx.stroke()
    // ctx.closePath()
  }

  render() {
    console.log("graphState", this.props.graphState)
    return (
      <div>
        <div id="query-builder">
          <ForceGraph2D
            graphData={this.props.graphState}
            width={this.w}
            height={this.h}
            // nodeLabel="label"
            backgroundColor="Gainsboro"
            onNodeClick={this.handleSelection}
            nodeCanvasObject={this.drawNode}
            // linkLabel="label"
            // linkWidth="1"
            // linkDirectionalArrowLength={5}
            // linkDirectionalArrowRelPos={1}
            linkCanvasObject={this.drawLink}

          />
        </div>
      </div>
      )
  }
}
