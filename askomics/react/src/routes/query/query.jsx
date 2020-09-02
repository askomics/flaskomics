import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button, Row, Col, ButtonGroup, Input, Spinner } from 'reactstrap'
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
import Utils from '../../classes/utils'

export default class Query extends Component {

  constructor (props) {
    super(props)
    this.utils = new Utils()
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
    this.specialNodeIdNumber = 0
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
    // init node id
    let listId = new Set()
    this.graphState.nodes.map(node => {
      listId.add(node.id)
    })

    this.graphState.links.map(link => {
      listId.add(link.id)
    })

    this.graphState.attr.map(attr => {
      listId.add(attr.id)
    })

    this.idNumber = Math.max(...listId)

    // init specialNode id
    let listSpecialId = new Set()
    this.graphState.nodes.map(node => {
      listSpecialId.add(node.specialNodeId)
    })
    this.specialNodeIdNumber = Math.max(...listSpecialId)
  }

  getId () {
    this.idNumber += 1
    return this.idNumber
  }

  getSpecialNodeId () {
    this.specialNodeIdNumber += 1
    return this.specialNodeIdNumber
  }

  getLargestSpecialNodeGroupId (node) {
    let listIds = new Set()
    this.graphState.links.map(link => {
      if (link.source.id == node.id) {
        listIds.add(link.target.specialNodeGroupId)
      }
      if (link.target.id == node.id) {
        listIds.add(link.source.specialNodeGroupId)
      }
    })
    return Math.max(...listIds)
  }

  getHumanNodeId (uri) {
    let humanIds = [0, ]
    this.graphState.nodes.map(node => {
      if (node.uri == uri) {
        humanIds.push(node.humanId)
      }
    })
    return Math.max(...humanIds) + 1
  }

  entityExist (uri) {
    return this.state.abstraction.entities.some(entity => {
      return (entity.uri == uri)
    })
  }

  getLabel (uri) {
    return this.state.abstraction.entities.map(node => {
      if (node.uri == uri) {
        return node.label
      } else {
        return null
      }
    }).filter(label => label != null).reduce(label => label)
  }

  getType (uri) {
    return this.state.abstraction.entities.map(node => {
      if (node.uri == uri) {
        return node.type
      } else {
        return null
      }
    }).filter(type => type != null).reduce(type => type)
  }

  getGraphs (uri) {
    return [...new Set(this.state.abstraction.attributes.flatMap(attr => {
      if (attr.entityUri == uri) {
        return attr.graphs
      }
    }).filter(graph => graph != null))]
  }


  getEntityUris (uri) {
    return [...new Set(this.state.abstraction.attributes.flatMap(attr => {
      if (attr.uri == uri) {
        return attr.entityUri
      }
    }).filter(entityUri => entityUri != null))]
  }

  getAttributeType (typeUri) {
    // FIXME: don't hardcode uri
    if (typeUri == 'http://www.w3.org/2001/XMLSchema#decimal') {
      return 'decimal'
    }
    if (typeUri == this.state.config.namespaceInternal + 'AskomicsCategory') {
      return 'category'
    }
    if (typeUri == 'http://www.w3.org/2001/XMLSchema#string') {
      return 'text'
    }
    if (typeUri == "http://www.w3.org/2001/XMLSchema#boolean") {
      return "boolean"
    }
  }

  attributeExistInAbstraction (attrUri, entityUri) {
    return this.state.abstraction.attributes.some(attr => {
      return (attr.uri == attrUri && attr.entityUri == entityUri)
    })
  }

  isBnode (nodeId) {
    return this.graphState.nodes.some(node => {
      return (node.id == nodeId && node.type == "bnode")
    })
  }

  isFaldoEntity (entityUri) {
    return this.state.abstraction.entities.some(entity => {
      return (entity.uri == entityUri && entity.faldo)
    })
  }

  attributeExist (attrUri, nodeId) {
    return this.graphState.attr.some(attr => {
      return (attr.uri == attrUri && attr.nodeId == nodeId)
    })
  }

  nodeHaveInstancesWithLabel (uri) {
    return this.state.abstraction.entities.some(entity => {
      return (entity.uri == uri && entity.instancesHaveLabels)
    })
  }

  getHumanIdFromId(nodeId) {
    return this.graphState.nodes.map(node => {
      if (node.id == nodeId) {
        return node.humanId
      } else {
        return null
      }
    }).filter(humanId => humanId != null).reduce(humanId => humanId)
  }

  count_displayed_attributes() {
    return this.graphState.attr.map(attr => {
      return attr.visible ? 1 : 0
    }).reduce((a, b) => a + b)
  }

  setNodeAttributes (nodeUri, nodeId) {
    let nodeAttributes = []
    let isBnode = this.isBnode(nodeId)

    // if bnode without uri, first attribute is visible
    let firstAttrVisibleForBnode = isBnode

    // if label don't exist, donc create a label attribute and set uri visible
    let labelExist = this.nodeHaveInstancesWithLabel(nodeUri)

    // create uri attributes
    if (!this.attributeExist('rdf:type', nodeId) && !isBnode) {
      nodeAttributes.push({
        id: this.getId(),
        visible: !labelExist,
        nodeId: nodeId,
        humanNodeId: this.getHumanIdFromId(nodeId),
        uri: 'rdf:type',
        label: 'Uri',
        entityLabel: this.getLabel(nodeUri),
        entityUris: [nodeUri, ],
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

    // create label attributes
    if (!this.attributeExist('rdfs:label', nodeId) && labelExist) {
      nodeAttributes.push({
        id: this.getId(),
        visible: true,
        nodeId: nodeId,
        humanNodeId: this.getHumanIdFromId(nodeId),
        uri: 'rdfs:label',
        label: 'Label',
        entityLabel: this.getLabel(nodeUri),
        entityUris: [nodeUri, ],
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

    // create other attributes
    nodeAttributes = nodeAttributes.concat(this.state.abstraction.attributes.map(attr => {
      let attributeType = this.getAttributeType(attr.type)
      if (attr.entityUri == nodeUri && !this.attributeExist(attr.uri, nodeId)) {
        let nodeAttribute = {
          id: this.getId(),
          visible: firstAttrVisibleForBnode,
          nodeId: nodeId,
          humanNodeId: this.getHumanIdFromId(nodeId),
          uri: attr.uri,
          label: attr.label,
          entityLabel: this.getLabel(nodeUri),
          entityUris: this.getEntityUris(attr.uri),
          type: attributeType,
          faldo: attr.faldo,
          optional: false,
          negative: false,
          linked: false,
          linkedWith: null
        }

        firstAttrVisibleForBnode = false

        if (attributeType == 'decimal') {
          nodeAttribute.filters = [
            {
              filterValue: "",
              filterSign: "="
            }
          ]
        }

        if (attributeType == 'text') {
          nodeAttribute.filterType = 'exact'
          nodeAttribute.filterValue = ''
        }

        if (attributeType == 'category') {
          nodeAttribute.filterValues = attr.categories
          nodeAttribute.filterSelectedValues = []
        }

        if (attributeType == 'boolean') {
          nodeAttribute.filterValues = ["true", "false"]
          nodeAttribute.filterSelectedValues = []
        }

        return nodeAttribute
      }
    }).filter(attr => {return attr != null}))

    // add attributes to the graph state
    this.graphState.attr = this.graphState.attr.concat(nodeAttributes)
  }

  insertNode (uri, selected, suggested, special=null, forceSpecialId=null, specialNodeGroupId=null, specialPreviousIds=[null, null]) {
    /*
    Insert a new node in the graphState
    */
    let nodeId = this.getId()
    let humanId = this.getHumanNodeId(uri)
    let specialNodeId = null

    if (special) {
      specialNodeId = this.getSpecialNodeId()
    }

    if (forceSpecialId) {
      specialNodeId = forceSpecialId
    }

    let node = {
      uri: uri,
      type: special ? special : this.getType(uri),
      filterNode: "",
      filterLink: "",
      graphs: this.getGraphs(uri),
      id: nodeId,
      humanId: humanId,
      specialNodeId: specialNodeId,
      specialNodeGroupId: specialNodeGroupId,
      specialPreviousIds: specialPreviousIds,
      label: this.getLabel(uri),
      faldo: this.isFaldoEntity(uri),
      selected: selected,
      suggested: suggested
    }
    this.graphState.nodes.push(node)
    if (selected) {
      this.previousSelected = this.currentSelected
      this.currentSelected = node
    }

    if (!suggested && !special) {
      this.setNodeAttributes(uri, nodeId)
    }
    return node
  }

  removeNode (id) {
    /*
    remove a node in the graphState
    */
    this.graphState.nodes = this.graphState.nodes.filter(node => node.id != id)
  }

  removeLink (id) {
    /*
    remove a link in the graphState
    */
    this.graphState.links = this.graphState.links.filter(link => link.id != id)
  }

  removeAttributes(id){
    /*
    remove node attributes in the graphState
    */
    this.graphState.attr = this.graphState.attr.filter(attr => attr.nodeId != id)
  }

  getNodesAndLinksIdToDelete (id, nodesAndLinks={nodes: [], links: []}) {
    /*
    recursively get nodes and link to remove from the graphState
    */
    this.graphState.links.map(link => {

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

  insertSuggestion (node, incrementSpecialNodeGroupId=null) {
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

    let specialNodeGroupId = incrementSpecialNodeGroupId ? incrementSpecialNodeGroupId : node.specialNodeGroupId

    this.state.abstraction.relations.map(relation => {
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
              specialNodeId: node.specialNodeId,
              specialNodeGroupId: specialNodeGroupId,
              specialPreviousIds: node.specialPreviousIds,
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
              strict: true,
              id: linkId,
              label: relation.label,
              source: node.id,
              target: targetId,
              selected: false,
              suggested: true,
              directed: true
            })
            incrementSpecialNodeGroupId ? specialNodeGroupId += 1 : specialNodeGroupId = specialNodeGroupId
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
              specialNodeId: node.specialNodeId,
              specialNodeGroupId: specialNodeGroupId,
              specialPreviousIds: node.specialPreviousIds,
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
              suggested: true,
              directed: true
            })
            incrementSpecialNodeGroupId ? specialNodeGroupId += 1 : specialNodeGroupId = specialNodeGroupId
          }
        }
      }
    })

    // Position
    if (node.faldo) {
      this.state.abstraction.entities.map(entity => {
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
            specialNodeId: node.specialNodeId,
            specialNodeGroupId: specialNodeGroupId,
            specialPreviousIds: node.specialPreviousIds,
            label: entity.label,
            faldo: entity.faldo,
            selected: false,
            suggested: true
          })
          // push suggested link
          this.graphState.links.push({
            uri: "included_in",
            type: "posLink",
            id: this.getId(),
            sameStrand: this.nodeHaveStrand(node.uri) && this.nodeHaveStrand(entity.uri),
            sameRef: this.nodeHaveRef(node.uri) && this.nodeHaveRef(entity.uri),
            strict: true,
            label: "Included in",
            source: node.id,
            target: new_id,
            selected: false,
            suggested: true,
            directed: true
          })
          incrementSpecialNodeGroupId ? specialNodeGroupId += 1 : specialNodeGroupId = specialNodeGroupId
        }
      })
    }
  }

  removeAllSuggestion () {
    let newNodes = this.graphState.nodes.filter(node => !node.suggested)
    let newLinks = this.graphState.links.filter(link => !link.suggested)
    let newAttr = this.graphState.attr
    this.graphState = {
      nodes: newNodes,
      links: newLinks,
      attr: newAttr
    }
  }

  insertLinkIfExists (node1, node2) {
    let newLink = {}

    this.graphState.links.map(link => {
      if (link.source.id == node1.id && link.target.id == node2.id) {
        newLink = {
          uri: link.uri,
          type: ["included_in", "overlap_with"].includes(link.uri) ? "posLink" : "link",
          sameStrand: this.nodeHaveStrand(node1.uri) && this.nodeHaveStrand(node2.uri),
          sameRef: this.nodeHaveRef(node1.uri) && this.nodeHaveRef(node2.uri),
          strict: true,
          id: this.getId(),
          label: link.label,
          source: node1.id,
          target: node2.id,
          selected: false,
          suggested: false,
          directed: true
        }
      }

      if (link.source.id == node2.id && link.target.id == node1.id) {
        newLink = {
          uri: link.uri,
          type: ["included_in", "overlap_with"].includes(link.uri) ? "posLink" : "link",
          sameStrand: this.nodeHaveStrand(node1.uri) && this.nodeHaveStrand(node2.uri),
          sameRef: this.nodeHaveRef(node1.uri) && this.nodeHaveRef(node2.uri),
          strict: true,
          id: this.getId(),
          label: link.label,
          source: node2.id,
          target: node1.id,
          selected: false,
          suggested: false,
          directed: true
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
    // get attributes (only for nodes)
    if (node.type =="node") {
      this.setNodeAttributes(node.uri, node.id)
    }
  }

  instanciateNode (node) {
    this.graphState.nodes.map(inode => {
      if (node.id == inode.id) {
        inode.suggested = false
      }
    })
    // get attributes (only for nodes)
    if (node.type =="node") {
      this.setNodeAttributes(node.uri, node.id)
    }
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
    // Only position link are clickabl
    if (clickedLink.type == "posLink") {
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

      // if node is a special node, get the greatest specialNodeGroupId
      if (clickedNode.type == "unionNode") {
        this.insertSuggestion(this.currentSelected, this.getLargestSpecialNodeGroupId(clickedNode) + 1)
      } else {
        this.insertSuggestion(this.currentSelected)
      }

    }
    // update graph state
    this.updateGraphState()
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

    // Remove current node and attributes
    this.removeNode(nodeIdToDelete)
    this.removeAttributes(nodeIdToDelete)

    // Get all nodes and link connected after the node to delete
    let nodeAndLinksToDelete = this.getNodesAndLinksIdToDelete(nodeIdToDelete)

    // remove all this nodes and links and their attributes
    nodeAndLinksToDelete.nodes.map(id => {
      this.removeNode(id)
      this.removeAttributes(id)
    })
    nodeAndLinksToDelete.links.map(id => {
      this.removeLink(id)
    })

    // unselect node
    this.manageCurrentPreviousSelected(null)

    // update graph
    this.updateGraphState()
  }

  setCurrentSelected () {
    this.graphState.nodes.map(node => {
      if (node.selected) {
        this.currentSelected = node
      }
    })
    this.graphState.links.map(link => {
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
    console.log(this.graphState)
  }

  initGraph () {
    this.insertNode(this.state.startpoint, true, false)
    this.insertSuggestion(this.currentSelected)
    this.updateGraphState()
  }

  // Node conversion
  handleNodeConversion(event, data) {
    /*
      Source node
      Special node
      Target node
    */
    let sourceNode = this.currentSelected

    // Get info about the relation between source and target
    let relation = this.getInfoAboutRelation(sourceNode.id, data.node.id)

    // remove suggestionand unselect all
    this.removeAllSuggestion()
    this.unselectAllObjects()

    // Get previous special node ids
    let specialPreviousIds = [sourceNode.specialNodeId, sourceNode.specialNodeGroupId]

    // insert a special node and select it
    let specialNode = this.insertNode(sourceNode.uri, true, false, data.convertTo, null, null, specialPreviousIds)

    // insert target node with specialNodeGroupId = 1
    let targetNode = this.insertNode(data.node.uri, false, false, null, specialNode.specialNodeId, 1, specialPreviousIds)

    // insert link between source and special node
    this.insertSpecialLink(sourceNode, specialNode, data.convertTo)

    // insert link between special node and target
    relation.source = relation.source == "source" ? specialNode.id : targetNode.id
    relation.target = relation.target == "target" ? targetNode.id : specialNode.id
    relation.id = this.getId()
    relation.suggested = false
    relation.selected = false
    this.graphState.links.push(relation)

    //insert suggestion with first specialNodeGroupId = 2 (will be incremented for each suggestion)
    this.insertSuggestion(specialNode, 2)

    // Manage selection
    this.manageCurrentPreviousSelected(specialNode)

    // Update graph
    this.updateGraphState()
  }

  getInfoAboutRelation(sourceId, targetId) {
    let relation
    this.graphState.links.map(link => {
      if ((link.source.id == sourceId && link.target.id == targetId) || link.source.id == targetId && link.target.id == sourceId) {
        relation =  {
          uri: link.uri,
          type: link.type,
          sameStrand: link.sameStrand,
          sameRef: link.sameRef,
          strict: link.strict,
          id: null,
          label: link.label,
          source: link.source.id == sourceId ? "source" : "target",
          target: link.target.id == targetId ? "target" : "source",
          selected: link.selected,
          suggested: link.suggested,
          directed: link.directed
        }
      }
    })
    return relation
  }

  insertSpecialLink(node1, node2, relation) {
    let link = {
      uri: null,
      type: "specialLink",
      sameStrand: null,
      sameRef: null,
      strict: null,
      id: this.getId(),
      label: relation == "unionNode" ? "Union" : "Not",
      source: node1.id,
      target: node2.id,
      selected: false,
      suggested: false,
      directed: false
    }
    this.graphState.links.push(link)
  }

  // Filter nodes --------------------------
  handleFilterNodes (event) {
    // Store the filter
    this.graphState.nodes.map(node => {
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
    this.graphState.nodes.map(node => {
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
    this.graphState.attr.map(attr => {
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
    this.graphState.attr.map(attr => {
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
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.negative = event.target.value == '=' ? false : true
      }
    })
    this.updateGraphState()
  }

  handleFilterType (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterType = event.target.value
      }
    })
    this.updateGraphState()
  }

  handleFilterValue (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterValue = event.target.value
      }
    })
    this.updateGraphState()
  }

  handleFilterCategory (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filterSelectedValues = [...event.target.selectedOptions].map(o => o.value)
      }
    })
    this.updateGraphState()
  }

  handleFilterNumericSign (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filters.map((filter, index) => {
          if (index == event.target.dataset.index) {
            filter.filterSign = event.target.value
          }
        })
      }
    })
    this.updateGraphState()
  }

  toggleAddNumFilter (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filters.push({
          filterValue: "",
          filterSign: "="
        })
      }
    })
    this.updateGraphState()
  }

  handleFilterNumericValue (event) {
    if (!isNaN(event.target.value)) {
      this.graphState.attr.map(attr => {
        if (attr.id == event.target.id) {
          attr.filters.map((filter, index) => {
            if (index == event.target.dataset.index) {
              filter.filterValue = event.target.value
            }
          })
        }
      })
      this.updateGraphState()
    }
  }

  toggleLinkAttribute (event) {
    this.graphState.attr.map(attr => {
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
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.linkedWith = parseInt(event.target.value)
      }
    })
    this.updateGraphState()
  }

  // Link view methods -----------------------------

  handleChangePosition (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.uri = event.target.value
        link.label = event.target.value == 'included_in' ? "Included in" : "Overlap with"
      }
    })
    this.updateGraphState()
  }

  mapLinks (event) {
    this.graphState.links.map(link => {})
    this.updateGraphState()
  }

  handleClickReverse (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        let old_target = link.target
        link.target = link.source
        link.source = old_target
      }
    })
    this.updateGraphState()
  }

  handleChangeSameRef (event) {
    this.graphState.links.map(link => {
      if ("sameref-" + link.id == event.target.id) {
        link.sameRef = event.target.checked
      }
    })
    this.updateGraphState()
  }

  handleChangeSameStrand (event) {
    this.graphState.links.map(link => {
      if ("samestrand-" + link.id == event.target.id) {
        link.sameStrand = event.target.checked
      }
    })
    this.updateGraphState()
  }

  handleChangeStrict (event) {
    this.graphState.links.map(link => {
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
      graphState: this.graphState
    }
    this.setState({
      disablePreview: true,
      previewIcon: "spinner"
    })

    // display an error message if user don't display attribute to avoid the virtuoso SPARQL error
    if (this.count_displayed_attributes() == 0) {
      this.setState({
        error: true,
        errorMessage: ["No attribute are displayed. Use eye icon to display at least one attribute", ],
        disablePreview: false,
        previewIcon: "times text-error"
      })
      return
    }

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
      graphState: this.graphState
    }

    // display an error message if user don't display attribute to avoid the virtuoso SPARQL error
    if (this.count_displayed_attributes() == 0) {
      this.setState({
        error: true,
        errorMessage: ["No attribute are displayed. Use eye icon to display at least one attribute", ],
        disableSave: false,
        saveIcon: "times text-error"
      })
      return
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
            if (this.currentSelected) {
              if (this.currentSelected.type != "link") {
                this.insertSuggestion(this.currentSelected)
              }
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
              Your files (uploaded files and results) take {this.utils.humanFileSize(this.state.diskSpace, true)} of space 
              (you have {this.utils.humanFileSize(this.state.config.user.quota, true)} allowed). 
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
      // attribute boxes (right view) only for node
      if (this.currentSelected) {
        AttributeBoxes = this.state.graphState.attr.map(attribute => {
          if (attribute.nodeId == this.currentSelected.id && this.currentSelected.type == "node") {
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
                toggleAddNumFilter={p => this.toggleAddNumFilter(p)}
              />
            )
          }
        })
        // Link view (rightview)
        if (this.currentSelected.type == "posLink") {

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
          handleNodeConversion={(p, d) => this.handleNodeConversion(p, d)}
        />
      )

      // buttons
      let previewIcon = <i className={"fas fa-" + this.state.previewIcon}></i>
      if (this.state.previewIcon == "spinner") {
        previewIcon = <Spinner size="sm" color="light" />
      }
      previewButton = <Button onClick={this.handlePreview} color="secondary" disabled={this.state.disablePreview}>{previewIcon} Run & preview</Button>
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
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} customMessages={{"504": "Query time is too long, use Run & Save to get your results", "502": "Query time is too long, use Run & Save to get your results"}} />
      </div>
    )
  }
}

Query.propTypes = {
  location: PropTypes.object,
  waitForStart: PropTypes.bool
}
