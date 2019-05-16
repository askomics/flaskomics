import React, { Component } from "react"
import axios from 'axios'
import { Alert, Button, Row, Col, ButtonGroup } from 'reactstrap';
import { Redirect} from 'react-router-dom'
import ErrorDiv from "../error/error"
import WaitingDiv from "../../components/waiting"
import update from 'react-addons-update'
import Visualization from './visualization'
import AttributeBox from './attribute'
import ResultsTable from '../sparql/resultstable'

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
        links: [],
        attr: []
      },
      resultsPreview: [],
      headerPreview: [],
      waiting: true,
      error: false,
      errorMessage: null,
    }

    this.graphState = {
      nodes: [],
      links: [],
      attr: []
    }

    this.divHeight = 650

    this.idNumber = 0
    this.previousSelected = null
    this.currentSelected = null
    this.cancelRequest

    this.handlePreview = this.handlePreview.bind(this)
    this.handleQuery = this.handleQuery.bind(this)
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

  getGraphs(uri) {
    let graphs = []
    this.state.abstraction.entities.forEach(node => {
      if (node.uri == uri) {
        graphs = graphs.concat(node.graphs)
      }
    })
    return graphs
  }

  getAttributeType(typeUri) {
    //FIXME: don't hardcode uri
    if (typeUri == "http://www.w3.org/2001/XMLSchema#decimal") {
      return "decimal"
    }
    if (typeUri == "http://www.semanticweb.org/user/ontologies/2018/1#AskomicsCategory") {
      return "category"
    }
    if (typeUri == "http://www.w3.org/2001/XMLSchema#string") {
      return "text"
    }
  }

  attributeExist(attrUri, nodeId) {
    let result = false
    this.state.graphState.attr.forEach(attr => {
      if (attr.uri == attrUri && attr.nodeId == nodeId) {
        result = true
      }
    })
    return result
  }

  setNodeAttributes(nodeUri, nodeId) {

    let nodeAttributes = []

    // create uri and label attributes
    if (!this.attributeExist("rdf:type", nodeId)) {
      nodeAttributes.push({
        id: this.getId(),
        visible: false,
        nodeId: nodeId,
        uri: "rdf:type",
        label: "Uri",
        entityLabel: this.getLabel(nodeUri),
        entityUri: nodeUri,
        type: "uri",
        filterType: "exact",
        filterValue: ""
      })
    }

    if (!this.attributeExist("rdfs:label", nodeId)) {
      nodeAttributes.push({
        id: this.getId(),
        visible: true,
        nodeId: nodeId,
        uri: "rdfs:label",
        label: "Label",
        entityLabel: this.getLabel(nodeUri),
        entityUri: nodeUri,
        type: "text",
        filterType: "exact",
        filterValue: ""
      })
    }

    this.state.abstraction.attributes.forEach(attr => {
      if (attr.entityUri == nodeUri) {
        if (!this.attributeExist(attr.uri, nodeId)) {
          let nodeAttribute = {}
          let attributeType = this.getAttributeType(attr.type)
          nodeAttribute.id = this.getId()
          nodeAttribute.visible = false
          nodeAttribute.nodeId = nodeId
          nodeAttribute.uri = attr.uri,
          nodeAttribute.label = attr.label,
          nodeAttribute.entityLabel = this.getLabel(nodeUri)
          nodeAttribute.entityUri = attr.entityUri,
          nodeAttribute.type = attributeType

          if (attributeType == "decimal") {
            nodeAttribute.filterSign = "="
            nodeAttribute.filterValue = ""
          }

          if (attributeType == "text") {
            nodeAttribute.filterType = "exact"
            nodeAttribute.filterValue = ""
          }

          if (attributeType == "category") {
            nodeAttribute.filterValues = attr.categories
            nodeAttribute.filterSelectedValues = []
          }
          // return nodeAttribute
          nodeAttributes.push(nodeAttribute)
        }
      }
    })
    this.graphState.attr = this.graphState.attr.concat(nodeAttributes)
  }

  insertNode(uri, selected, suggested) {
    /*
    Insert a new node in the graphState
    */
    let nodeId = this.getId()
    let node = {
      uri: uri,
      graphs: this.getGraphs(uri),
      id: nodeId,
      label: this.getLabel(uri),
      selected: selected,
      suggested: suggested
    }
    this.graphState.nodes.push(node)
    if (selected) {
      this.currentSelected = node
    }

    if (!suggested) {
      this.setNodeAttributes(uri, nodeId)
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
            graphs: this.getGraphs(relation.target),
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
            graphs: this.getGraphs(relation.source),
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
    let newAttr = this.graphState.attr
    this.graphState = {
      nodes: newNodes,
      links: newLinks,
      attr: newAttr
    }
  }

  insertLinkIfExists(node1, node2) {

    let link = {}

    this.state.abstraction.relations.forEach(relation => {
      if (relation.source == node1.uri && relation.target == node2.uri) {
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

  manageCurrentPreviousSelected(currentNode) {
      this.previousSelected = this.currentSelected
      this.currentSelected = currentNode
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
    // get attributes
    this.setNodeAttributes(node.uri, node.id)
    }



  handleNodeSelection(clickedNode) {

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
      let suggested = clickedNode.suggested
      // update current and previous
      this.manageCurrentPreviousSelected(clickedNode)
      // unselect all nodes
      this.unselectAllNodes()
      // select and instanciate the new node
      this.selectAndInstanciateNode(clickedNode)
      // remove all suggestion
      this.removeAllSuggestion()
      // instanciate link only if clicked node is suggested
      if (suggested) {
        this.insertLinkIfExists(this.currentSelected, this.previousSelected)
      }
      // insert suggestion
      this.insertSuggestion(this.currentSelected)

    }
    // update graph state
    this.updateGraphState()
  }

  setCurrentSelected() {
    this.graphState.nodes.forEach(node => {
      if (node.selected) {
        this.currentSelected = node
      }
    })
  }

  updateGraphState() {
    this.setState({
      graphState: this.graphState
    })
  }

  initGraph() {
    this.insertNode(this.state.startpoint, true, false)
    this.insertSuggestion(this.currentSelected)
    this.updateGraphState()
  }

  // Attributes managment -----------------------
  toggleVisibility(event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.visible = !attr.visible
      }
    })
    this.updateGraphState()
  }

  toggleFilterType(event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterType = attr.filterType == "exact" ? "regexp" : "exact"
      }
    })
    this.updateGraphState()
  }

  handleFilterValue(event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterValue = event.target.value
      }
    })
    this.updateGraphState()
  }


  handleFilterCategory(event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterSelectedValues = [...event.target.selectedOptions].map(o => o.value)
      }
    })
    this.updateGraphState()
  }


  handleFilterNumericSign(event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterSign = event.target.value
      }
    })

    this.updateGraphState()
  }


  handleFilterNumericValue(event) {
    if (!isNaN(event.target.value)) {
      this.state.graphState.attr.map(attr => {
        if (attr.id == event.target.id) {
          attr.filterValue = event.target.value
        }
      })
      this.updateGraphState()
    }
  }

  // ------------------------------------------------

  // Preview results and Launch query buttons -------

  handlePreview(event) {
    let requestUrl = '/api/query/preview'
    let data = {
      graphState: this.state.graphState
    }
    axios.post(requestUrl, data, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        resultsPreview: response.data.resultsPreview,
        headerPreview: response.data.headerPreview,
        waiting: false,
        error: false
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status
      })
    })
  }

  handleQuery(event) {
    let requestUrl = '/api/query/save_result'
    let data = {
      graphState: this.state.graphState
    }
    axios.post(requestUrl, data, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
    .then(response => {
      console.log(requestUrl, response.data)
    }).catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status
      })
    })
  }

  // ------------------------------------------------

  componentDidMount() {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/query/abstraction'
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
          status: error.response.status
        })
      }).then(response => {
        if (this.props.location.state.redo) {
          // redo a query
          this.graphState = this.props.location.state.graphState
          this.setCurrentSelected()
          this.updateGraphState()
        }else{
          this.initGraph()
        }
        this.setState({waiting: false})
      })
    }
  }

  componentWillUnmount() {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  render() {
    // login page redirection
    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    // error div
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

    let visualizationDiv
    let uriLabelBoxes
    let AttributeBoxes
    let buttons

    if (!this.state.waiting) {
      // attribute boxes (right view)
      if (this.currentSelected) {
        AttributeBoxes = this.state.graphState.attr.map(attribute => {
          if (attribute.nodeId == this.currentSelected.id) {
            return (
              <AttributeBox
                attribute={attribute}
                toggleVisibility={p => this.toggleVisibility(p)}
                toggleFilterType={p => this.toggleFilterType(p)}
                handleFilterValue={p => this.handleFilterValue(p)}
                handleFilterCategory={p => this.handleFilterCategory(p)}
                handleFilterNumericSign={p => this.handleFilterNumericSign(p)}
                handleFilterNumericValue={p => this.handleFilterNumericValue(p)}
              />
            )
          }
        })
      }

      // visualization (left view)
      visualizationDiv = (
        <Visualization
          divHeight={this.divHeight}
          abstraction={this.state.abstraction}
          graphState={this.state.graphState}
          logged={this.state.logged}
          user={this.state.user}
          waiting={this.state.waiting}
          handleNodeSelection={p => this.handleNodeSelection(p)}
        />
      )

      // buttons
      buttons = (
        <ButtonGroup>
          <Button onClick={this.handlePreview} color="secondary">Preview results</Button>
          <Button onClick={this.handleQuery} color="secondary">Launch Query</Button>
        </ButtonGroup>
      )
    }

    // preview
    let resultsTable
    if (this.state.resultsPreview.length > 0) {
      resultsTable = (
        <ResultsTable data={this.state.resultsPreview} header={this.state.headerPreview} />
      )
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>Query Builder</h2>
        <hr />
        <WaitingDiv waiting={this.state.waiting} center />
        <Row>
          <Col xs="7">
          <div>
            {visualizationDiv}
          </div>
          </Col>
          <Col xs="5">
          <div style={{display: "block", height: this.divHeight + "px", "overflow-y": "auto"}}>
            {uriLabelBoxes}
            {AttributeBoxes}
          </div>
          </Col>
        </Row>
        {buttons}
        <br /> <br />
        <div>
          {resultsTable}
        </div>
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}