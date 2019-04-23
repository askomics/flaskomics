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
    return (
      <div>
        <div id="query-builder">
          <ForceGraph2D
            graphData={this.props.graphState}
            width={this.w}
            height={this.h}
            nodeLabel="label"
            backgroundColor="Gainsboro"
            onNodeClick={node => {
              let newGraphState = this.props.graphState
              newGraphState.nodes.map(inode => {
                if (inode == node) {
                  inode.selected = !inode.selected
                }
              })
              this.props.setStateAsk({
                graphState: newGraphState
              })
            }}
            nodeCanvasObject={(node, ctx, globalScale) => {
                  // node style
                  ctx.fillStyle = this.stringToHexColor(node.uri)
                  ctx.beginPath()
                  ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false)
                  // stroke style
                  ctx.strokeStyle = node.selected ? this.colorFirebrick : this.colorGrey
                  // build node
                  ctx.stroke()
                  ctx.fill()
                }}
          />
        </div>
      </div>
      )
  }
}
