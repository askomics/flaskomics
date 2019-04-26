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
    this.colorFirebrick = "#cc0000"

    this.cancelRequest
    this.handleSelection = this.props.handleSelection.bind(this)
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

  render() {
    console.log("graphState", this.props.graphState)
    return (
      <div>
        <div id="query-builder">
          <ForceGraph2D
            graphData={this.props.graphState}
            width={this.w}
            height={this.h}
            nodeLabel="label"
            backgroundColor="Gainsboro"
            onNodeClick={this.handleSelection}
            nodeCanvasObject={(node, ctx, globalScale) => {
              // node style
              ctx.fillStyle = this.stringToHexColor(node.uri)
              ctx.beginPath()
              ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI, false)
              // stroke style
              ctx.strokeStyle = node.selected ? this.colorFirebrick : this.colorGrey
              ctx.globalAlpha = node.suggested ? 0.5 : 1
              // text
              // ctx.font = '5px Sans-Serif'
              // ctx.textAlign = 'middle'
              // ctx.textBaseline = 'middle'
              // ctx.fillText(node.label, node.x + 2, node.y + 8)
              // build node
              ctx.stroke()
              ctx.fill()
            }}
            linkLabel="label"
            // linkWidth="1"
            linkDirectionalArrowLength={5}
            linkDirectionalArrowRelPos={1}
            linkCanvasObject={(link, ctx, globalScale) => {
              ctx.moveTo(link.source.x, link.source.y)
              ctx.lineTo(link.target.x, link.target.y)
              ctx.strokeStyle = this.colorGrey
              ctx.globalAlpha = link.suggested ? 0.5 : 1
              ctx.stroke()
              // arrow




            }}

          />
        </div>
      </div>
      )
  }
}
