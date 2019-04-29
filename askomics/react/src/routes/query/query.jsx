import React, { Component } from "react"
import axios from 'axios'
import { Alert, Button } from 'reactstrap';
import { Redirect} from 'react-router-dom'
import ErrorDiv from "../error/error"
import WaitingDiv from "../../components/waiting"
import update from 'react-addons-update'
import Visualization from './visualization'

export default class Query extends Component {

  constructor(props) {
    super(props)
    this.state = {
      logged: this.props.location.state.logged,
      user: this.props.location.state.user,
      startpoint: this.props.location.state.startpoint,
      abstraction: [],
      graphState: {
        nodes: [],
        links: []
      },
      waiting: true,
      error: false,
      errorMessage: null,
    }
    this.graphState = {
      nodes: [],
      links: []
    }
    this.idNumber = 0
    this.previousSelected = null
    this.currentSelected = null
    this.cancelRequest
  }

  getId() {
    this.idNumber += 1
      return this.idNumber
    }

  entityExist(uri) {
    let result = false
    this.state.abstraction.entities.forEach(entity => {
      if (entity.uri == uri) {
        result = true
      }
    })
    return result
  }

  getLabel(uri) {
    let label = this.state.abstraction.entities.map(node => {
      if (node.uri == uri) {
        return node.label
      }else {
        return null
      }
    }).filter(label => label != null).reduce(label => label)
    return label
  }

  insertNode(uri, selected, suggested) {
    /*
    Insert a new node in the graphState
    */    
    let node = {
      uri: uri,
      id: this.getId(),
      label: this.getLabel(uri),
      selected: selected,
      suggested: suggested
    }
    this.graphState.nodes.push(node)
    if (selected) {
      this.currentSelected = node
    }
  }

  insertSuggestion(node) {
    /*
    Insert suggestion for this node

    Browse abstraction.relation to find all neighbor of node.
    Insert the node as unselected and suggested
    Create the (suggested) link between this node and the suggestion
    */
    let targetId
    let sourceId
    let linkId
    this.state.abstraction.relations.forEach(relation => {
      if (relation.source == node.uri) {
        if (this.entityExist(relation.target)) {
          targetId = this.getId()
          linkId = this.getId()
          // Push suggested target
          this.graphState.nodes.push({
            uri: relation.target,
            id: targetId,
            label: this.getLabel(relation.target),
            selected: false,
            suggested: true
          })
          // push suggested link
          this.graphState.links.push({
            uri: relation.uri,
            id: linkId,
            label: relation.label,
            source: node.id,
            target: targetId,
            selected: false,
            suggested: true
          })
        }
      }

      if (relation.target == node.uri) {
        if (this.entityExist(relation.source)) {
          sourceId = this.getId()
          linkId = this.getId()
          // Push suggested source
          this.graphState.nodes.push({
            uri: relation.source,
            id: sourceId,
            label: this.getLabel(relation.source),
            selected: false,
            suggested: true
          })
          // push suggested link
          this.graphState.links.push({
            uri: relation.uri,
            id: this.getId(),
            label: relation.label,
            source: sourceId,
            target: node.id,
            selected: false,
            suggested: true
          })
        }
      }
    })
  }

  removeAllSuggestion() {
    let newNodes = this.graphState.nodes.filter(node => {
      if (!node.suggested) {
        return node
      }
    })
    let newLinks = this.graphState.links.filter(link => {
      if (!link.suggested) {
        return link
      }
    })
    this.graphState = {
      nodes: newNodes,
      links: newLinks
    }
  }

  insertLinkIfExists(node1, node2) {

    let link = {}

    this.state.abstraction.relations.forEach(relation => {
      if (relation.source == node1.uri && relation.target == node2.uri) {
        console.log("insert link " + node1.label + " --> " + node2.label)
        link = {
          uri: relation.uri,
          id: this.getId(),
          label: relation.label,
          source: node1.id,
          target: node2.id,
          selected: false,
          suggested: false
        }
      }

      if (relation.source == node2.uri && relation.target == node1.uri) {
        console.log("insert link " + node1.label + " <-- " + node2.label)
        link = {
          uri: relation.uri,
          id: this.getId(),
          label: relation.label,
          source: node2.id,
          target: node1.id,
          selected: false,
          suggested: false
        }
      }

    })
    this.graphState.links.push(link)
  }

  manageCurrentPreviousSelected(currentUri) {
      this.previousSelected = this.currentSelected
      this.currentSelected = currentUri
  }

  unselectAllNodes() {
    this.graphState.nodes.map(node => {
      node.selected = false
    })
  }

selectAndInstanciateNode(node) {
    this.graphState.nodes.map(inode => {
      if (node.id == inode.id) {
        inode.selected = true
        inode.suggested = false
      }
    })
  }



  handleSelection(clickedNode) {

    // case 1 : clicked node is selected, so deselect it
    if (clickedNode.selected) {
      // update current and previous
      this.manageCurrentPreviousSelected(null)

      // deselect all
      this.unselectAllNodes()

      // remove all suggestion
      this.removeAllSuggestion()
    } else {
      // case 2: clicked node is unselected, so select it

      // update current and previous
      this.manageCurrentPreviousSelected(clickedNode)
      // unselect all nodes
      this.unselectAllNodes()
      // select and instanciate the new node
      this.selectAndInstanciateNode(clickedNode)
      // remove all suggestion
      this.removeAllSuggestion()
      // instanciate link
      if (this.previousSelected) {
        this.insertLinkIfExists(this.currentSelected, this.previousSelected)
      }
      // insert suggestion
      this.insertSuggestion(this.currentSelected)

    }
    // update graph state
    this.updateGraphState()
  }

  updateGraphState() {
    console.log("graphState", this.graphState)
    this.setState({
      graphState: this.graphState
    })
  }

  initGraph() {
    this.insertNode(this.state.startpoint, true, false)
    this.insertSuggestion(this.currentSelected)
    this.updateGraphState()
  }

  componentDidMount() {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/startpoints/abstraction'
      axios.get(requestUrl, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
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
          status: error.response.status,
          waiting: false
        })
      }).then(response => {
        this.initGraph()
      })
    }
  }

  componentWillUnmount() {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  render() {
    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    let errorDiv
    if (this.state.error) {
      errorDiv = (
        <div>
          <Alert color="danger">
            <i className="fas fa-exclamation-circle"></i> {this.state.errorMessage}
          </Alert>
        </div>
      )
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>Query Builder</h2>
        <hr />
        <WaitingDiv waiting={this.state.waiting} center />
        <Visualization
          abstraction={this.state.abstraction}
          startpoint={this.state.startpoint}
          graphState={this.state.graphState}
          logged={this.state.logged}
          user={this.state.user}
          waiting={this.state.waiting}
          setStateAsk={p => this.setState(p)}
          handleSelection={p => this.handleSelection(p)}
        />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}