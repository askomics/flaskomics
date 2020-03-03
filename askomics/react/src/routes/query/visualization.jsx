import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import { ForceGraph2D } from 'react-force-graph'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'
import { ContextMenu, MenuItem, ContextMenuTrigger } from "react-contextmenu";

export default class Visualization extends Component {
  constructor (props) {
    super(props)
    this.state = {
      error: false,
      errorMessage: null
    }

    this.utils = new Utils()

    // graph constants
    this.fg
    this.w = 650
    this.h = this.props.divHeight
    this.zoom = 5
    this.zoomTime = 1000
    this.colorGrey = '#808080'
    this.colorDarkGrey = '#404040'
    this.colorFirebrick = '#cc0000'
    this.colorGreen = '#005500FF'
    this.lineWidth = 0.5
    this.nodeSize = 3
    this.blankNodeSize = 1
    this.arrowLength = 7

    this.contextTrigger = null
    this.rightClickedNodeId = null

    this.cancelRequest
    this.handleNodeSelection = this.props.handleNodeSelection.bind(this)
    this.handleLinkSelection = this.props.handleLinkSelection.bind(this)
    this.drawNode = this.drawNode.bind(this)
    this.drawLink = this.drawLink.bind(this)

    this.handleRightClick = this.handleRightClick.bind(this)
    this.handleRightClickMenu = this.handleRightClickMenu.bind(this)
  }

  IntersectionCoordinate (x1, y1, x2, y2, r) {
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
    return { x: x, y: y }
  }

  middleCoordinate (x1, y1, x2, y2) {
    let theta = Math.atan((y2 - y1) / (x1 - x2))
    let x
    let y
    if (x1 < x2) {
      x = x1 + (this.nodeSize * 4) * Math.cos(theta)
      y = y1 - (this.nodeSize * 4) * Math.sin(theta)
    } else {
      x = x1 - (this.nodeSize * 4) * Math.cos(theta)
      y = y1 + (this.nodeSize * 4) * Math.sin(theta)
    }
    return { x: x, y: y }
  }

  triangleCoordinate (x1, y1, x2, y2, headlen) {
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

  subNums (id) {
    let newStr = ""
    let oldStr = id.toString()
    let arrayString = [...oldStr]
    arrayString.forEach(char => {
      let code = char.charCodeAt()
      newStr += String.fromCharCode(code + 8272)
    })
    return newStr
  }



  drawNode (node, ctx, globalScale) {
    // node style
    let unselectedColor = node.faldo ? this.colorGreen : this.colorGrey
    let unselectedColorText = node.faldo ? this.colorGreen : this.colorDarkGrey
    ctx.fillStyle = node.type == "node" ? this.utils.stringToHexColor(node.uri) : "#ffffff"
    ctx.lineWidth = this.lineWidth
    ctx.strokeStyle = node.selected ? this.colorFirebrick : unselectedColor
    ctx.globalAlpha = node.suggested ? 0.5 : 1
    node.suggested ? ctx.setLineDash([this.lineWidth, this.lineWidth]) : ctx.setLineDash([])
    // draw node
    ctx.beginPath()
    ctx.arc(node.x, node.y, this.nodeSize, 0, 2 * Math.PI, false)
    ctx.stroke()
    ctx.fill()
    ctx.closePath()
    // draw text
    ctx.beginPath()
    ctx.fillStyle = unselectedColorText
    ctx.font = this.nodeSize + 'px Sans-Serif'
    ctx.textAlign = 'middle'
    ctx.textBaseline = 'middle'
    let label = node.humanId ? node.label + " " + this.subNums(node.humanId) : node.label
    ctx.fillText(label, node.x + this.nodeSize, node.y + this.nodeSize)
    ctx.closePath()
  }

  drawLink (link, ctx, globalScale) {
    // link style
    link.suggested ? ctx.setLineDash([this.lineWidth, this.lineWidth]) : ctx.setLineDash([])

    let greenArray = ["included_in", "overlap_with"]
    let unselectedColor = greenArray.indexOf(link.uri) >= 0 ? this.colorGreen : this.colorGrey
    let unselectedColorText = greenArray.indexOf(link.uri) >= 0 ? this.colorGreen : this.colorDarkGrey
    ctx.strokeStyle = link.selected ? this.colorFirebrick : unselectedColor

    ctx.fillStyle = link.selected ? this.colorFirebrick : greenArray.indexOf(link.uri) >= 0 ? this.colorGreen : this.colorGrey
    ctx.globalAlpha = link.suggested ? 0.3 : 1
    ctx.lineWidth = this.lineWidth
    // draw link (from source to target)
    ctx.beginPath()
    let c = this.IntersectionCoordinate(link.source.x, link.source.y, link.target.x, link.target.y, this.nodeSize)
    ctx.moveTo(c.x, c.y)
    c = this.IntersectionCoordinate(link.target.x, link.target.y, link.source.x, link.source.y, this.nodeSize)
    ctx.lineTo(c.x, c.y)
    ctx.stroke()
    ctx.closePath()
    // draw arrow
    ctx.beginPath()
    let triangle = this.triangleCoordinate(link.target.x, link.target.y, link.source.x, link.source.y, this.arrowLength)
    ctx.moveTo(c.x, c.y)
    ctx.lineTo(triangle.xa, triangle.ya)
    ctx.lineTo(triangle.xb, triangle.yb)
    ctx.fill()
    ctx.closePath()
    // draw text
    ctx.beginPath()
    ctx.fillStyle = unselectedColorText
    ctx.font = this.nodeSize - 0.5 + 'px Sans-Serif'
    ctx.textAlign = 'middle'
    ctx.textBaseline = 'middle'
    let m = this.middleCoordinate(link.source.x, link.source.y, link.target.x, link.target.y)
    ctx.fillText(link.label, m.x, m.y)
    ctx.closePath()
  }

  handleRightClick(clickedNode, event) {
    if (this.contextTrigger && clickedNode.suggested) {
      this.setState({
        rightClickedNodeId: clickedNode.id
      })
      this.contextTrigger.handleContextClick(event)
    }
  }

  handleRightClickMenu(event, data) {
    console.log("Convert " + data.nodeId + " to " + data.convertTo + " node")
  }

  componentDidMount () {
    this.fg.zoom(this.zoom, this.zoomTime)
  }

  render () {
    return (
      <div>
        <ForceGraph2D
          ref={element => { this.fg = element }}
          graphData={this.props.graphState}
          width={this.w}
          height={this.h}
          backgroundColor="Gainsboro"
          onNodeClick={this.handleNodeSelection}
          onNodeRightClick={this.handleRightClick}
          onLinkClick={this.handleLinkSelection}
          nodeCanvasObject={this.drawNode}
          linkCanvasObject={this.drawLink}
        />

    <div>
      <ContextMenuTrigger id="context-menu-1" ref={c => this.contextTrigger = c}>
      </ContextMenuTrigger>

      <ContextMenu id="context-menu-1">
        <MenuItem data={{nodeId: this.state.rightClickedNodeId, convertTo: "union"}} onClick={this.handleRightClickMenu}>
          Convert to UNION node
        </MenuItem>
        <MenuItem data={{nodeId: this.state.rightClickedNodeId, convertTo: "not"}} onClick={this.handleRightClickMenu}>
          Convert to NOT node
        </MenuItem>
      </ContextMenu>
    </div>

      </div>
    )
  }
}

Visualization.propTypes = {
  divHeight: PropTypes.number,
  handleNodeSelection: PropTypes.object,
  handleLinkSelection: PropTypes.object,
  graphState: PropTypes.object
}
