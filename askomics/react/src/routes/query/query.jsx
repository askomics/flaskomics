import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button, Row, Col, ButtonGroup, Input } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import Visualization from './visualization'
import AttributeBox from './attribute'
import LinkView from './linkview'
import GraphFilters from './graphfilters'
import ResultsTable from '../sparql/resultstable'
import PropTypes from 'prop-types'

export default class Query extends Component {

  constructor (props) {
    super(props)
    this.state = {
      config: this.props.location.state.config,
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
      saveTick: false,

      // save query icons
      disableSave: false,
      saveIcon: "play",

      // Preview icons
      disablePreview: false,
      previewIcon: "table"
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
    this.handleRemoveNode = this.handleRemoveNode.bind(this)
    this.handleFilterNodes = this.handleFilterNodes.bind(this)
    this.handleFilterLinks = this.handleFilterLinks.bind(this)
  }

  resetIcons() {
    this.setState({
      previewIcon: "table"
    })
  }

  initId () {
    let listId = new Set()
    this.graphState.nodes.forEach(node => {
      listId.add(node.id)
    })

    this.graphState.links.forEach(link => {
      listId.add(link.id)
    })

    this.graphState.attr.forEach(attr => {
      listId.add(attr.id)
    })

    this.idNumber = Math.max(...listId)
  }

  getId () {
    this.idNumber += 1
    return this.idNumber
  }

  getHumanNodeId (uri) {
    let humanIds = [0, ]
    this.state.graphState.nodes.map(node => {
      if (node.uri == uri) {
        humanIds.push(node.humanId)
      }
    })
    return Math.max(...humanIds) + 1
  }

  entityExist (uri) {
    let result = false
    this.state.abstraction.entities.forEach(entity => {
      if (entity.uri == uri) {
        result = true
      }
    })
    return result
  }

  getLabel (uri) {
    let label = this.state.abstraction.entities.map(node => {
      if (node.uri == uri) {
        return node.label
      } else {
        return null
      }
    }).filter(label => label != null).reduce(label => label)
    return label
  }

  getType (uri) {
    let type = this.state.abstraction.entities.map(node => {
      if (node.uri == uri) {
        return node.type
      } else {
        return null
      }
    }).filter(type => type != null).reduce(type => type)
    return type
  }

  getGraphs (uri) {
    let graphs = []
    this.state.abstraction.entities.forEach(node => {
      if (node.uri == uri) {
        graphs = graphs.concat(node.graphs)
      }
    })
    return graphs
  }

  getAttributeType (typeUri) {
    // FIXME: don't hardcode uri
    if (typeUri == 'http://www.w3.org/2001/XMLSchema#decimal') {
      return 'decimal'
    }
    if (typeUri == this.state.config.prefix + 'AskomicsCategory') {
      return 'category'
    }
    if (typeUri == 'http://www.w3.org/2001/XMLSchema#string') {
      return 'text'
    }
  }

  attributeExistInAbstraction (attrUri, entityUri) {
    let result = false
    this.state.abstraction.attributes.forEach(attr => {
      if (attr.uri == attrUri && attr.entityUri == entityUri) {
        result = true
      }
    })
    return result
  }

  isBnode (nodeId) {
    let result = false
    this.state.graphState.nodes.forEach(node => {
      if (node.id == nodeId && node.type == "bnode") {
        result = true
      }
    })
    return result
  }

  isFaldoEntity (entityUri) {
    let result = false
    this.state.abstraction.entities.forEach(entity => {
      if (entity.uri == entityUri && entity.faldo) {
        result = true
      }
    })
    return result
  }

  attributeExist (attrUri, nodeId) {
    let result = false
    this.state.graphState.attr.forEach(attr => {
      if (attr.uri == attrUri && attr.nodeId == nodeId) {
        result = true
      }
    })
    return result
  }

  setNodeAttributes (nodeUri, nodeId) {
    let nodeAttributes = []
    let isBnode = this.isBnode(nodeId)

    // if bnode without uri, first attribute is visible
    let firstAttrVisibleForBnode = isBnode

    // create uri and label attributes
    if (!this.attributeExist('rdf:type', nodeId) && !isBnode) {
      nodeAttributes.push({
        id: this.getId(),
        visible: false,
        nodeId: nodeId,
        uri: 'rdf:type',
        label: 'Uri',
        entityLabel: this.getLabel(nodeUri),
        entityUri: nodeUri,
        type: 'uri',
        faldo: false,
        filterType: 'exact',
        filterValue: '',
        optional: false,
        negative: false,
        linked: false,
        linkedWith: null
      })
    }

    if (!this.attributeExist('rdfs:label', nodeId) && !isBnode) {
      nodeAttributes.push({
        id: this.getId(),
        visible: true,
        nodeId: nodeId,
        uri: 'rdfs:label',
        label: 'Label',
        entityLabel: this.getLabel(nodeUri),
        entityUri: nodeUri,
        type: 'text',
        faldo: false,
        filterType: 'exact',
        filterValue: '',
        optional: false,
        negative: false,
        linked: false,
        linkedWith: null
      })
      firstAttrVisibleForBnode = false
    }

    this.state.abstraction.attributes.forEach(attr => {
      if (attr.entityUri == nodeUri) {
        if (!this.attributeExist(attr.uri, nodeId)) {
          let nodeAttribute = {}
          let attributeType = this.getAttributeType(attr.type)
          nodeAttribute.id = this.getId()
          nodeAttribute.visible = firstAttrVisibleForBnode
          nodeAttribute.nodeId = nodeId
          nodeAttribute.uri = attr.uri
          nodeAttribute.label = attr.label
          nodeAttribute.entityLabel = this.getLabel(nodeUri)
          nodeAttribute.entityUri = attr.entityUri
          nodeAttribute.type = attributeType
          nodeAttribute.faldo = attr.faldo
          nodeAttribute.optional = false
          nodeAttribute.negative = false
          nodeAttribute.linked = false
          nodeAttribute.linkedWith = null

          firstAttrVisibleForBnode = false

          if (attributeType == 'decimal') {
            nodeAttribute.filterSign = '='
            nodeAttribute.filterValue = ''
          }

          if (attributeType == 'text') {
            nodeAttribute.filterType = 'exact'
            nodeAttribute.filterValue = ''
          }

          if (attributeType == 'category') {
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

  insertNode (uri, selected, suggested) {
    /*
    Insert a new node in the graphState
    */
    let nodeId = this.getId()
    let humanId = this.getHumanNodeId(uri)
    let node = {
      uri: uri,
      type: this.getType(uri),
      filterNode: "",
      filterLink: "",
      graphs: this.getGraphs(uri),
      id: nodeId,
      humanId: humanId,
      label: this.getLabel(uri),
      faldo: this.isFaldoEntity(uri),
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

  removeNode (id) {
    /*
    remove a node in the graphState
    */
    this.graphState.nodes.forEach((node, index, gstate) => {
      if (node.id == id) {
        gstate.splice(index, 1)
      }
    })
  }

  removeLink (id) {
    /*
    remove a link in the graphState
    */
    this.graphState.links.forEach((link, index, gstate) => {
      if (link.id == id) {
        gstate.splice(index, 1)
      }
    })
  }

  removeAttributes(id){
    this.state.graphState.attr.forEach((attr, index, gstate) => {
      if (attr.nodeId == id) {
        gstate.splice(index, 1)
      }
    })
  }

  getNodesAndLinksIdToDelete (id, nodesAndLinks={nodes: [], links: []}) {
    /*
    recusriveky get nodes and link to remove from the graphState
    */
    this.graphState.links.forEach(link => {

      if (link.target.id == id) {
        if (link.source.id > id) {
          nodesAndLinks.nodes.push(link.source.id)
          nodesAndLinks.links.push(link.id)
          nodesAndLinks = this.getNodesAndLinksIdToDelete(link.source.id, nodesAndLinks)
        } else {
          nodesAndLinks.links.push(link.id)
        }
      }
      if (link.source.id == id) {
        if (link.target.id > id) {
          nodesAndLinks.nodes.push(link.target.id)
          nodesAndLinks.links.push(link.id)
          nodesAndLinks = this.getNodesAndLinksIdToDelete(link.target.id, nodesAndLinks)
        } else {
          nodesAndLinks.links.push(link.id)
        }
      }
    })
    return nodesAndLinks
  }

  insertSuggestion (node) {
    /*
    Insert suggestion for this node

    Browse abstraction.relation to find all neighbor of node.
    Insert the node as unselected and suggested
    Create the (suggested) link between this node and the suggestion
    */
    let targetId
    let sourceId
    let linkId
    let label
    let resFilterNode
    let resFilterLink

    let reNode = new RegExp(node.filterNode, 'g')
    let reLink = new RegExp(node.filterLink, 'g')

    this.state.abstraction.relations.forEach(relation => {
      if (relation.source == node.uri) {
        if (this.entityExist(relation.target)) {
          targetId = this.getId()
          linkId = this.getId()
          label = this.getLabel(relation.target)
          resFilterNode = label.toLowerCase().match(reNode)
          resFilterLink = relation.label.toLowerCase().match(reLink)
          if (resFilterNode && resFilterLink) {
            // Push suggested target
            this.graphState.nodes.push({
              uri: relation.target,
              type: this.getType(relation.target),
              filterNode: "",
              filterLink: "",
              graphs: this.getGraphs(relation.target),
              id: targetId,
              humanId: null,
              label: label,
              faldo: this.isFaldoEntity(relation.target),
              selected: false,
              suggested: true
            })
            // push suggested link
            this.graphState.links.push({
              uri: relation.uri,
              type: "link",
              sameStrand: this.nodeHaveStrand(node.uri) && this.nodeHaveStrand(relation.target),
              sameRef: this.nodeHaveRef(node.uri) && this.nodeHaveRef(relation.target),
              id: linkId,
              label: relation.label,
              source: node.id,
              target: targetId,
              selected: false,
              suggested: true
            })
          }
        }
      }

      if (relation.target == node.uri) {
        if (this.entityExist(relation.source)) {
          sourceId = this.getId()
          linkId = this.getId()
          label = this.getLabel(relation.source)
          resFilterNode = label.toLowerCase().match(reNode)
          resFilterLink = relation.label.toLowerCase().match(reLink)
          if (resFilterNode && resFilterLink) {
            // Push suggested source
            this.graphState.nodes.push({
              uri: relation.source,
              type: this.getType(relation.source),
              filterNode: "",
              filterLink: "",
              graphs: this.getGraphs(relation.source),
              id: sourceId,
              humanId: null,
              label: label,
              faldo: this.isFaldoEntity(relation.source),
              selected: false,
              suggested: true
            })
            // push suggested link
            this.graphState.links.push({
              uri: relation.uri,
              type: "link",
              sameStrand: this.nodeHaveStrand(node.id) && this.nodeHaveStrand(relation.source),
              sameRef: this.nodeHaveRef(node.id) && this.nodeHaveRef(relation.source),
              id: this.getId(),
              label: relation.label,
              source: sourceId,
              target: node.id,
              selected: false,
              suggested: true
            })
          }
        }
      }
    })

    // Position
    if (node.faldo) {
      this.state.abstraction.entities.forEach(entity => {
        if (entity.faldo) {
          let new_id = this.getId()
          // Push suggested target
          this.graphState.nodes.push({
            uri: entity.uri,
            type: this.getType(entity.uri),
            filterNode: "",
            filterLink: "",
            graphs: this.getGraphs(entity.uri),
            id: new_id,
            humanId: null,
            label: entity.label,
            faldo: entity.faldo,
            selected: false,
            suggested: true
          })
          // push suggested link
          this.graphState.links.push({
            uri: "included_in",
            type: "link",
            id: this.getId(),
            sameStrand: this.nodeHaveStrand(node.uri) && this.nodeHaveStrand(entity.uri),
            sameRef: this.nodeHaveRef(node.uri) && this.nodeHaveRef(entity.uri),
            strict: true,
            label: "Included in",
            source: node.id,
            target: new_id,
            selected: false,
            suggested: true
          })
        }
      })
    }
  }

  removeAllSuggestion () {
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

  insertLinkIfExists (node1, node2) {
    let newLink = {}

    this.state.graphState.links.forEach(link => {
      if (link.source.id == node1.id && link.target.id == node2.id) {
        newLink = {
          uri: link.uri,
          type: "link",
          sameStrand: this.nodeHaveStrand(node1.uri) && this.nodeHaveStrand(node2.uri),
          sameRef: this.nodeHaveRef(node1.uri) && this.nodeHaveRef(node2.uri),
          strict: true,
          id: this.getId(),
          label: link.label,
          source: node1.id,
          target: node2.id,
          selected: false,
          suggested: false
        }
      }

      if (link.source.id == node2.id && link.target.id == node1.id) {
        newLink = {
          uri: link.uri,
          type: "link",
          sameStrand: this.nodeHaveStrand(node1.uri) && this.nodeHaveStrand(node2.uri),
          sameRef: this.nodeHaveRef(node1.uri) && this.nodeHaveRef(node2.uri),
          strict: true,
          id: this.getId(),
          label: link.label,
          source: node2.id,
          target: node1.id,
          selected: false,
          suggested: false
        }
      }
    })
    this.graphState.links.push(newLink)
  }

  manageCurrentPreviousSelected (currentObject) {
    this.previousSelected = this.currentSelected
    this.currentSelected = currentObject
  }

  unselectAllNodes () {
    this.graphState.nodes.map(node => {
      node.selected = false
    })
  }

  unselectAllLinks () {
    this.graphState.links.map(link => {
      link.selected = false
    })
  }

  unselectAllObjects () {
    this.unselectAllNodes()
    this.unselectAllLinks()
  }

  selectAndInstanciateNode (node) {
    this.graphState.nodes.map(inode => {
      if (node.id == inode.id) {
        inode.selected = true
        inode.suggested = false
        inode.humanId = inode.humanId ? inode.humanId : this.getHumanNodeId(inode.uri)
      }
    })
    // get attributes
    this.setNodeAttributes(node.uri, node.id)
  }

  instanciateNode (node) {
    this.graphState.nodes.map(inode => {
      if (node.id == inode.id) {
        inode.suggested = false
      }
    })
    // get attributes
    this.setNodeAttributes(node.uri, node.id)
  }

  selectAndInstanciateLink (link) {
    this.graphState.links.map(ilinks => {
      if (link.id == ilinks.id) {
        ilinks.selected = true
        ilinks.suggested = false
      }
    })
  }

  handleLinkSelection (clickedLink) {
    // case 1: link is selected, so deselect it
    if (clickedLink.selected) {
      // Update current and previous
      this.manageCurrentPreviousSelected(null)

      // Deselect nodes and links
      this.unselectAllObjects()

      // Remove all suggestion
      this.removeAllSuggestion()
    } else {
      // case 2: link is unselected, so select it
      let suggested = clickedLink.suggested
      // Update current and previous
      this.manageCurrentPreviousSelected(clickedLink)
      // Deselect nodes and links
      this.unselectAllObjects()
      // Select and instanciate the link
      this.selectAndInstanciateLink(clickedLink)
      // instanciate node only if node is suggested
      if (suggested) {
        this.instanciateNode(clickedLink.target)
      }
      // reload suggestions
      this.removeAllSuggestion()
    }
    this.updateGraphState()
  }

  handleNodeSelection (clickedNode) {
    // case 1 : clicked node is selected, so deselect it
    if (clickedNode.selected) {
      // update current and previous
      this.manageCurrentPreviousSelected(null)

      // Deselect nodes and links
      this.unselectAllObjects()

      // remove all suggestion
      this.removeAllSuggestion()
    } else {
      // case 2: clicked node is unselected, so select it
      let suggested = clickedNode.suggested
      // update current and previous
      this.manageCurrentPreviousSelected(clickedNode)
      // Deselect nodes and links
      this.unselectAllObjects()
      // select and instanciate the new node
      this.selectAndInstanciateNode(clickedNode)
      // instanciate link only if clicked node is suggested
      if (suggested) {
        this.insertLinkIfExists(this.currentSelected, this.previousSelected)
      }
      // remove all suggestion
      this.removeAllSuggestion()
      // insert suggestion
      this.insertSuggestion(this.currentSelected)
    }
    // update graph state
    this.updateGraphState()
    // // manage node filter
    // this.manageFilterNodes(this.currentSelected.filter)
  }

  handleRemoveNode () {

    if (this.currentSelected == null) {
      console.log("No node selected")
      return
    }

    if (this.currentSelected.id == 1) {
      console.log("AskOmics can't delete the startpoint")
      return
    }

    let nodeIdToDelete
    if (this.currentSelected.type == "link") {
      if (this.currentSelected) {}
      nodeIdToDelete =  Math.max(this.currentSelected.target.id, this.currentSelected.source.id)
    } else {
      nodeIdToDelete = this.currentSelected.id
    }

    this.removeNode(nodeIdToDelete)

    let nodeAndLinksToDelete = this.getNodesAndLinksIdToDelete(nodeIdToDelete)

    nodeAndLinksToDelete.nodes.forEach(id => {
      this.removeNode(id)
    })
    nodeAndLinksToDelete.links.forEach(id => {
      this.removeLink(id)
    })
    // remove attributes
    this.removeAttributes(nodeIdToDelete)

    // unselect node
    this.manageCurrentPreviousSelected(null)
    this.updateGraphState()
  }

  setCurrentSelected () {
    this.graphState.nodes.forEach(node => {
      if (node.selected) {
        this.currentSelected = node
      }
    })
    this.graphState.links.forEach(link => {
      if (link.selected) {
        this.currentSelected = link
      }
    })
  }

  updateGraphState (waiting=this.state.waiting) {
    this.setState({
      graphState: this.graphState,
      previewIcon: "table",
      resultsPreview: [],
      headerPreview: [],
      disableSave: false,
      disablePreview: false,
      saveIcon: "play",
      waiting: waiting
    })
  }

  initGraph () {
    this.insertNode(this.state.startpoint, true, false)
    this.insertSuggestion(this.currentSelected)
    this.updateGraphState()
  }


  // Filter nodes --------------------------
  handleFilterNodes (event) {
    // Store the filter
    this.state.graphState.nodes.map(node => {
      if (this.currentSelected.id == node.id) {
        node.filterNode = event.target.value
      }
    })
    // Reset suggestion
    this.removeAllSuggestion()
    this.insertSuggestion(this.currentSelected)
    this.updateGraphState()
  }


  // Filter links --------------------------
  handleFilterLinks (event) {
    // Store the filter
    this.state.graphState.nodes.map(node => {
      if (this.currentSelected.id == node.id) {
        node.filterLink = event.target.value
      }
    })
    // Reset suggestion
    this.removeAllSuggestion()
    this.insertSuggestion(this.currentSelected)
    this.updateGraphState()
  }

  // Attributes managment -----------------------
  toggleVisibility (event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.visible = !attr.visible
        if (!attr.visible) {
          attr.optional = false
        }
      }
    })
    this.updateGraphState()
  }

  toggleOptional (event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.optional = !attr.optional
        if (attr.optional) {
          attr.visible = true
        }
      }
    })
    this.updateGraphState()
  }

  handleNegative (event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.negative = event.target.value == '=' ? false : true
      }
    })
    this.updateGraphState()
  }

  handleFilterType (event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterType = event.target.value
      }
    })
    this.updateGraphState()
  }

  handleFilterValue (event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterValue = event.target.value
      }
    })
    this.updateGraphState()
  }

  handleFilterCategory (event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterSelectedValues = [...event.target.selectedOptions].map(o => o.value)
      }
    })
    this.updateGraphState()
  }

  handleFilterNumericSign (event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterSign = event.target.value
      }
    })

    this.updateGraphState()
  }

  handleFilterNumericValue (event) {
    if (!isNaN(event.target.value)) {
      this.state.graphState.attr.map(attr => {
        if (attr.id == event.target.id) {
          attr.filterValue = event.target.value
        }
      })
      this.updateGraphState()
    }
  }

  toggleLinkAttribute (event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.linked = !attr.linked
        if (!attr.linked) {
          attr.linkedWith = null
        }
      }
    })
    this.updateGraphState()
  }

  handleChangeLink (event) {
    this.state.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.linkedWith = parseInt(event.target.value)
      }
    })
    this.updateGraphState()
  }

  // Link view methods -----------------------------

  handleChangePosition (event) {
    this.state.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.uri = event.target.value
        link.label = event.target.value == 'included_in' ? "Included in" : "Overlap with"
      }
    })
    this.updateGraphState()
  }

  mapLinks (event) {
    this.state.graphState.links.map(link => {})
    this.updateGraphState()
  }

  handleClickReverse (event) {
    this.state.graphState.links.map(link => {
      if (link.id == event.target.id) {
        let old_target = link.target
        link.target = link.source
        link.source = old_target
      }
    })
    this.updateGraphState()
  }

  handleChangeSameRef (event) {
    this.state.graphState.links.map(link => {
      if ("sameref-" + link.id == event.target.id) {
        link.sameRef = event.target.checked
      }
    })
    this.updateGraphState()
  }

  handleChangeSameStrand (event) {
    this.state.graphState.links.map(link => {
      if ("samestrand-" + link.id == event.target.id) {
        link.sameStrand = event.target.checked
      }
    })
    this.updateGraphState()
  }

  handleChangeStrict (event) {
    this.state.graphState.links.map(link => {
      if ("strict-" + link.id == event.target.id) {
        link.strict = event.target.checked
      }
    })
    this.updateGraphState()
  }

  nodesHaveRefs (link) {
    let result = this.nodeHaveRef(link.source.uri) && this.nodeHaveRef(link.target.uri)
    if (! result) {
      link.sameRef = false
    }
    return result
  }

  nodeHaveRef (uri) {
    let result = false
    this.state.abstraction.attributes.map(attr => {
      if (uri == attr.entityUri && attr.faldo) {
        if (attr.faldo.endsWith("faldoReference")) {
          result =  true
        }
      }
    })
    return result
  }

  nodesHaveStrands (link) {
    let result = this.nodeHaveStrand(link.source.uri) && this.nodeHaveStrand(link.target.uri)
    if (! result) {
      link.sameStrand = false
    }
    return result
  }

  nodeHaveStrand (uri) {
    let result = false
    this.state.abstraction.attributes.map(attr => {
      if (uri == attr.entityUri && attr.faldo) {
        if (attr.faldo.endsWith("faldoStrand")) {
          result =  true
        }
      }
    })
    return result
  }

  // ------------------------------------------------

  // Preview results and Launch query buttons -------

  handlePreview (event) {
    let requestUrl = '/api/query/preview'
    let data = {
      graphState: this.state.graphState
    }
    this.setState({
      disablePreview: true,
      previewIcon: "spinner"
    })
    axios.post(requestUrl, data, { baseURL: this.state.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          resultsPreview: response.data.resultsPreview,
          headerPreview: response.data.headerPreview,
          waiting: false,
          error: false,
          previewIcon: "check text-success"
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          disablePreview: false,
          previewIcon: "times text-error"
        })
      })
  }

  handleQuery (event) {
    let requestUrl = '/api/query/save_result'
    let data = {
      graphState: this.state.graphState
    }
    axios.post(requestUrl, data, { baseURL: this.state.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          saveIcon: "check text-success",
          disableSave: true
        })
      }).catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
          saveIcon: "times text-error",
          disableSave: false
        })
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
            diskSpace: response.data.diskSpace,
            exceededQuota: this.state.config.user.quota > 0 && response.data.diskSpace >= this.state.config.user.quota,
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
            this.initId()
            this.setCurrentSelected()
            if (this.currentSelected.type != "link") {
              this.insertSuggestion(this.currentSelected)
            }
            this.updateGraphState()
          } else {
            this.initGraph()
          }
          this.setState({ waiting: false })
        })
    }
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  humanFileSize (bytes, si) {
    let thresh = si ? 1000 : 1024
    if (Math.abs(bytes) < thresh) {
      return bytes + ' B'
    }
    let units = si ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'] : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    let u = -1
    do {
      bytes /= thresh
      ++u
    } while (Math.abs(bytes) >= thresh && u < units.length - 1)
    return bytes.toFixed(1) + ' ' + units[u]
  }

  render () {
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

    // Warning disk space
    let warningDiskSpace
    if (this.state.exceededQuota) {
      warningDiskSpace = (
        <div>
          <Alert color="warning">
              Your files (uploaded files and results) take {this.humanFileSize(this.state.diskSpace, true)} of space 
              (you have {this.humanFileSize(this.state.config.user.quota, true)} allowed). 
              Please delete some before save queries or contact an admin to increase your quota
          </Alert>
        </div>
      )
    }

    let visualizationDiv
    let uriLabelBoxes
    let AttributeBoxes
    let linkView
    let previewButton
    let launchQueryButton
    let removeButton
    let graphFilters

    if (!this.state.waiting) {
      // attribute boxes (right view)
      if (this.currentSelected) {
        AttributeBoxes = this.state.graphState.attr.map(attribute => {
          if (attribute.nodeId == this.currentSelected.id) {
            return (
              <AttributeBox
                attribute={attribute}
                graph={this.state.graphState}
                handleChangeLink={p => this.handleChangeLink(p)}
                toggleVisibility={p => this.toggleVisibility(p)}
                handleNegative={p => this.handleNegative(p)}
                toggleOptional={p => this.toggleOptional(p)}
                handleFilterType={p => this.handleFilterType(p)}
                handleFilterValue={p => this.handleFilterValue(p)}
                handleFilterCategory={p => this.handleFilterCategory(p)}
                handleFilterNumericSign={p => this.handleFilterNumericSign(p)}
                handleFilterNumericValue={p => this.handleFilterNumericValue(p)}
                toggleLinkAttribute={p => this.toggleLinkAttribute(p)}
              />
            )
          }
        })
        // Link view (rightview)
        if (this.currentSelected.type == "link") {

          let link = Object.assign(this.currentSelected)
          this.state.graphState.nodes.map(node => {
            if (node.id == this.currentSelected.target) {
              link.target = node
            }
            if (node.id == this.currentSelected.source) {
              link.source = node
            }
          })

          linkView = <LinkView
            link={link}
            handleChangePosition={p => this.handleChangePosition(p)}
            handleClickReverse={p => this.handleClickReverse(p)}
            handleChangeSameRef={p => this.handleChangeSameRef(p)}
            handleChangeSameStrand={p => this.handleChangeSameStrand(p)}
            handleChangeStrict={p => this.handleChangeStrict(p)}
            nodesHaveRefs={p => this.nodesHaveRefs(p)}
            nodesHaveStrands={p => this.nodesHaveStrands(p)}
          />
        }
      }

      // visualization (left view)
      visualizationDiv = (
        <Visualization
          divHeight={this.divHeight}
          abstraction={this.state.abstraction}
          graphState={this.state.graphState}
          config={this.state.config}
          waiting={this.state.waiting}
          handleNodeSelection={p => this.handleNodeSelection(p)}
          handleLinkSelection={p => this.handleLinkSelection(p)}
        />
      )

      // buttons
      previewButton = <Button onClick={this.handlePreview} color="secondary" disabled={this.state.disablePreview}><i className={"fas fa-" + this.state.previewIcon}></i> Run & preview</Button>
      if (this.state.config.logged) {
        launchQueryButton = <Button onClick={this.handleQuery} color="secondary" disabled={this.state.disableSave || this.state.exceededQuota}><i className={"fas fa-" + this.state.saveIcon}></i> Run & save</Button>
      }
      if (this.currentSelected != null) {
        removeButton = (
          <ButtonGroup>
            <Button disabled={this.currentSelected.id == 1 ? true : false} onClick={this.handleRemoveNode} color="secondary" size="sm">Remove {this.currentSelected.type == "link" ? "Link" : "Node"}</Button>
          </ButtonGroup>
        )
      }

      // Filters
      graphFilters = (
        <GraphFilters
          graph={this.state.graphState}
          current={this.currentSelected}
          handleFilterNodes={this.handleFilterNodes}
          handleFilterLinks={this.handleFilterLinks}
        />
      )


    }

    // preview
    let resultsTable
    if (this.state.headerPreview.length > 0) {
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
            {graphFilters}
          </Col>
          <Col xs="5">
            {removeButton}
          </Col>
        </Row>
        <br />
        <Row>
          <Col xs="7">
            <div>
              {visualizationDiv}
            </div>
          </Col>
          <Col xs="5">
            <div style={{ display: 'block', height: this.divHeight + 'px', 'overflow-y': 'auto' }}>
              {uriLabelBoxes}
              {AttributeBoxes}
              {linkView}
            </div>
          </Col>
        </Row>
        {warningDiskSpace}
        <ButtonGroup>
          {previewButton}
          {launchQueryButton}
        </ButtonGroup>
        <br /> <br />
        <div>
          {resultsTable}
        </div>
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

Query.propTypes = {
  location: PropTypes.object,
  waitForStart: PropTypes.bool
}
