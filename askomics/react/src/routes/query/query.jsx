import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button, CustomInput, Row, Col, ButtonGroup, Input, Spinner, ButtonToolbar } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import { Tooltip } from 'react-tooltip'
import Visualization from './visualization'
import AttributeBox from './attribute'
import LinkView from './linkview'
import OntoLinkView from './ontolinkview'
import OverviewModal from './overviewModal'
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
      previewIcon: "table",
      ontologies: this.props.location.state.config.ontologies
    }

    this.graphState = {
      nodes: [],
      links: [],
      attr: []
    }

    this.divHeight = 650
    this.showFaldo = true;

    this.defaultFaldoFilters = [{
      filterValue: null,
      filterSign: "=",
      filterModifier: "+",
      filterStart: "start",
      filterEnd: "start"
    }]

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
    this.handleFilterFaldo = this.handleFilterFaldo.bind(this)
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

  getLargestSpecialNodeGroupId (node, preRender=false) {
    let listIds = new Set()
    let remote

    this.graphState.links.map(link => {
      if (preRender) {
      // Ugly, but before rendering source and target are IDs and not objects
        if (link.source == node.id) {
          remote = this.state.nodes.some(rem => {
            return (link.target == rem.id )
          })
          listIds.add(remote.specialNodeGroupId)
        }
        if (link.target == node.id) {
          remote = this.state.nodes.some(rem => {
            return (link.source == rem.id )
          })
          listIds.add(remote.specialNodeGroupId)
        }
      } else {
        if (link.source.id == node.id) {
          listIds.add(link.target.specialNodeGroupId)
        }
        if (link.target.id == node.id) {
          listIds.add(link.source.specialNodeGroupId)
        }
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

    const numURI = [
      "http://www.w3.org/2001/XMLSchema#decimal",
      "http://www.w3.org/2001/XMLSchema#integer",
      "http://www.w3.org/2001/XMLSchema#numeric",
      "http://www.w3.org/2001/XMLSchema#float",
    ]

    if (numURI.includes(typeUri)) {
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
    if (typeUri == "http://www.w3.org/2001/XMLSchema#date") {
      return "date"
    }
    // Default to text (Fallback for ttl integration with non-managed entity types)
    return "text"
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

  isRemoteOnto (currentUri, targetUri) {

    let node = this.state.abstraction.entities.find(entity => {
      return entity.uri == targetUri
    })

    if (! node){
      return false
    }

    return node.ontology ? currentUri == targetUri ? "endNode" : "node" : false
  }

  isOntoNode (currentId) {

    return this.graphState.nodes.some(node => {
      return (node.id == currentId && node.ontology)
    })
  }

  isOntoEndNode (currentId) {

    return this.graphState.nodes.some(node => {
      return (node.id == currentId && node.ontology == "endNode")
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

  nodeHaveDefaultVisibleAttribute (uri) {
      return this.state.abstraction.entities.flatMap(entity => {
        return (entity.uri == uri && entity.defaultVisible) ? [entity.defaultVisible] : []
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

    let isOnto = this.isOntoNode(nodeId)

    // if bnode without uri, first attribute is visible
    let firstAttrVisibleForBnode = isBnode

    // if label don't exist, donc create a label attribute and set uri visible
    let labelExist = this.nodeHaveInstancesWithLabel(nodeUri)
    let defaultVisible = this.nodeHaveDefaultVisibleAttribute(nodeUri)

    // create uri attributes
    if (!this.attributeExist('rdf:type', nodeId) && !isBnode) {
      nodeAttributes.push({
        id: this.getId(),
        visible: !(labelExist || defaultVisible.length),
        nodeId: nodeId,
        humanNodeId: this.getHumanIdFromId(nodeId),
        uri: 'rdf:type',
        label: 'Uri',
        displayLabel: 'Uri',
        entityLabel: this.getLabel(nodeUri),
        entityDisplayLabel: this.getLabel(nodeUri),
        entityUris: [nodeUri, ],
        type: 'uri',
        faldo: false,
        filterType: 'exact',
        filterValue: '',
        optional: false,
        form: false,
        negative: false,
        linked: false,
        linkedWith: null,
        ontology: isOnto
      })
    }

    // create label attributes
    if (!this.attributeExist('rdfs:label', nodeId) && (labelExist && !defaultVisible.length)) {
      nodeAttributes.push({
        id: this.getId(),
        visible: true,
        nodeId: nodeId,
        humanNodeId: this.getHumanIdFromId(nodeId),
        uri: 'rdfs:label',
        label: 'Label',
        displayLabel: 'Label',
        entityLabel: this.getLabel(nodeUri),
        entityDisplayLabel: this.getLabel(nodeUri),
        entityUris: [nodeUri, ],
        type: 'text',
        faldo: false,
        filterType: 'exact',
        filterValue: '',
        optional: false,
        form: false,
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
          visible: firstAttrVisibleForBnode || defaultVisible.includes(attr.uri),
          nodeId: nodeId,
          humanNodeId: this.getHumanIdFromId(nodeId),
          uri: attr.uri,
          label: attr.label,
          displayLabel: attr.displayLabel ? attr.displayLabel : attr.label,
          entityLabel: this.getLabel(nodeUri),
          entityDisplayLabel: attr.entityDisplayLabel ? attr.entityDisplayLabel : this.getLabel(nodeUri),
          entityUris: this.getEntityUris(attr.uri),
          type: attributeType,
          faldo: attr.faldo,
          optional: false,
          form: false,
          negative: false,
          linked: false,
          linkedWith: null
        }

        firstAttrVisibleForBnode = false

        if (attributeType == 'decimal') {
          nodeAttribute.filters = nodeAttribute.linkedFilters = [
            {
              filterValue: "",
              filterSign: "=",
              filterModifier: "+"
            }
          ]
        }

        if (attributeType == 'text') {
          nodeAttribute.filterType = 'exact'
          nodeAttribute.linkedNegative = false
          nodeAttribute.filterValue = nodeAttribute.linkedFilterValue = ''
        }

        if (attributeType == 'category') {
          nodeAttribute.exclude = false
          nodeAttribute.linkedNegative = false
          nodeAttribute.filterValues = attr.categories
          nodeAttribute.filterSelectedValues = []
        }

        if (attributeType == 'boolean') {
          nodeAttribute.filterValues = ["true", "false"]
          nodeAttribute.linkedNegative = false
          nodeAttribute.filterSelectedValues = []
        }

        if (attributeType == 'date') {
          nodeAttribute.filters = nodeAttribute.linkedFilters = [
            {
              filterValue: null,
              filterSign: "=",
              filterModifier: "+"
            }
          ]
        }

        return nodeAttribute
      }
    }).filter(attr => {return attr != null}))

    // add attributes to the graph state
    this.graphState.attr = this.graphState.attr.concat(nodeAttributes)
  }

  insertNode (uri, selected, suggested, special=null, forceSpecialId=null, specialNodeGroupId=null, specialPreviousIds=[null, null], newDepth=[]) {
    /*
    Insert a new node in the graphState
    */
    let nodeId = this.getId()
    let humanId = this.getHumanNodeId(uri)
    let specialNodeId = null

    let depth = [...newDepth]

    if (special) {
      specialNodeId = this.getSpecialNodeId()
    }

    if (special == "minusNode"){
      depth = [...newDepth, specialNodeId, specialNodeId + "_1"]
    }

    if (forceSpecialId) {
      specialNodeId = forceSpecialId
      depth = [...depth, forceSpecialId, forceSpecialId + "_" + specialNodeGroupId]
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
      depth: depth,
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

    let reNode = new RegExp(node.filterNode.toLowerCase(), 'g')
    let reLink = new RegExp(node.filterLink.toLowerCase(), 'g')

    let specialNodeGroupId = incrementSpecialNodeGroupId ? incrementSpecialNodeGroupId : node.specialNodeGroupId
    let depth = [...node.depth]

    if(incrementSpecialNodeGroupId){
      depth = [...node.depth, node.specialNodeId, node.specialNodeId + "_" + incrementSpecialNodeGroupId]
    }

    if (this.isOntoEndNode(node.id)){
        return
    }

    this.state.abstraction.relations.map(relation => {
      let isOnto = false
      if (relation.source == node.uri) {
        if (this.entityExist(relation.target)) {
          isOnto = this.isRemoteOnto(relation.source, relation.target)
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
              suggested: true,
              ontology: isOnto,
              depth: depth
            })
            // push suggested link
            this.graphState.links.push({
              uri: relation.uri,
              type: isOnto == "endNode" ? "ontoLink" : "link",
              sameStrand: this.nodeHaveStrand(node.uri) && this.nodeHaveStrand(relation.target),
              sameRef: this.nodeHaveRef(node.uri) && this.nodeHaveRef(relation.target),
              strict: false,
              id: linkId,
              label: relation.label,
              source: node.id,
              target: targetId,
              selected: false,
              suggested: true,
              directed: true,
              faldoFilters: this.defaultFaldoFilters,
              indirect: relation.indirect,
              isRecursive: relation.recursive,
              recursive: false,
            })
            incrementSpecialNodeGroupId ? specialNodeGroupId += 1 : specialNodeGroupId = specialNodeGroupId
            if (incrementSpecialNodeGroupId){
              depth = [...node.depth, node.specialNodeId, node.specialNodeId + "_" + incrementSpecialNodeGroupId]
            }
          }
        }
      }

      if (relation.target == node.uri) {
        if (this.entityExist(relation.source)) {
          isOnto = this.isRemoteOnto(relation.source, relation.target)
          if (! isOnto || relation.source == node.uri){
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
                suggested: true,
                ontology: isOnto,
                depth: depth
              })
              // push suggested link
              this.graphState.links.push({
                uri: relation.uri,
                type: isOnto == "endNode" ? "ontoLink" : "link",
                sameStrand: this.nodeHaveStrand(node.id) && this.nodeHaveStrand(relation.source),
                sameRef: this.nodeHaveRef(node.id) && this.nodeHaveRef(relation.source),
                id: this.getId(),
                label: relation.label,
                source: sourceId,
                target: node.id,
                selected: false,
                suggested: true,
                directed: true,
                faldoFilters: this.defaultFaldoFilters,
                indirect: relation.indirect,
                isRecursive: relation.recursive,
                recursive: false,
              })
              incrementSpecialNodeGroupId ? specialNodeGroupId += 1 : specialNodeGroupId = specialNodeGroupId
              if (incrementSpecialNodeGroupId){
                depth = [...node.depth, node.specialNodeId, node.specialNodeId + "_" + incrementSpecialNodeGroupId]
              }
            }
          }
        }
      }
    })

    // Position
    if (node.faldo && this.showFaldo) {
      this.state.abstraction.entities.map(entity => {
        if (entity.faldo) {
          let new_id = this.getId()
          resFilterNode = entity.label.toLowerCase().match(reNode)
          resFilterLink = "Included in".toLowerCase().match(reLink)
          if (resFilterNode && resFilterLink) {
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
              suggested: true,
              depth: depth
            })
            // push suggested link
            this.graphState.links.push({
              uri: "included_in",
              type: "posLink",
              id: this.getId(),
              sameStrand: this.nodeHaveStrand(node.uri) && this.nodeHaveStrand(entity.uri),
              sameRef: this.nodeHaveRef(node.uri) && this.nodeHaveRef(entity.uri),
              strict: false,
              label: "Included in",
              source: node.id,
              target: new_id,
              selected: false,
              suggested: true,
              directed: true,
              faldoFilters: this.defaultFaldoFilters,
              indirect: false,
              isRecursive: false,
              recursive: false,
            })
            incrementSpecialNodeGroupId ? specialNodeGroupId += 1 : specialNodeGroupId = specialNodeGroupId
            if (incrementSpecialNodeGroupId){
              depth = [...node.depth, node.specialNodeId, node.specialNodeId + "_" + incrementSpecialNodeGroupId]
            }
          }
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
          // What's the point of this?
          // type: ["included_in", "overlap_with"].includes(link.uri) ? "posLink" :  "link",
          type: link.type,
          sameStrand: this.nodeHaveStrand(node1.uri) && this.nodeHaveStrand(node2.uri),
          sameRef: this.nodeHaveRef(node1.uri) && this.nodeHaveRef(node2.uri),
          strict: false,
          id: this.getId(),
          label: link.label,
          source: node1.id,
          target: node2.id,
          selected: false,
          suggested: false,
          directed: link.directed,
          faldoFilters: link.faldoFilters ? link.faldoFilters :  this.defaultFaldoFilters,
          indirect: link.indirect ? link.indirect : false,
          isRecursive: link.isRecursive ? link.isRecursive : false,
          recursive: link.recursive ? link.recursive : false,
        }
      }

      if (link.source.id == node2.id && link.target.id == node1.id) {
        newLink = {
          uri: link.uri,
          // What's the point of this?
          // type: ["included_in", "overlap_with"].includes(link.uri) ? "posLink" :  "link",
          type: link.type,
          sameStrand: this.nodeHaveStrand(node1.uri) && this.nodeHaveStrand(node2.uri),
          sameRef: this.nodeHaveRef(node1.uri) && this.nodeHaveRef(node2.uri),
          strict: false,
          id: this.getId(),
          label: link.label,
          source: node2.id,
          target: node1.id,
          selected: false,
          suggested: false,
          directed: link.directed,
          faldoFilters: link.faldoFilters ? link.faldoFilters :  this.defaultFaldoFilters,
          indirect: link.indirect ? link.indirect : false,
          isRecursive: link.isRecursive ? link.isRecursive : false,
          recursive: link.recursive ? link.recursive : false,
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
        inode.humanId = inode.humanId ? inode.humanId : this.getHumanNodeId(inode.uri)
      }
    })
    // get attributes (only for nodes)
    if (node.type == "node") {
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
    if (clickedLink.type == "posLink" || clickedLink.type == "ontoLink") {
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
          if (clickedLink.target.suggested){
            this.instanciateNode(clickedLink.target)
          }
          if (clickedLink.source.suggested){
            this.instanciateNode(clickedLink.source)
          }
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

    let depth
    if (this.currentSelected.type == "unionNode"){
      depth = [...sourceNode.depth, sourceNode.specialNodeId, sourceNode.specialNodeId + "_" + this.getLargestSpecialNodeGroupId(sourceNode) + 1]
    } else {
      depth = [...sourceNode.depth]
    }

    // insert a special node and select it
    let specialNode = this.insertNode(sourceNode.uri, true, false, data.convertTo, null, null, specialPreviousIds, depth)

    // insert target node with specialNodeGroupId = 1
    let targetNode = this.insertNode(data.node.uri, false, false, null, specialNode.specialNodeId, 1, specialPreviousIds, depth)

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
    if (this.currentSelected.type == "unionNode"){
      this.insertSuggestion(specialNode, 2)
    } else {
      this.insertSuggestion(specialNode)
    }

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
          directed: link.directed,
          faldoFilters: link.faldoFilters,
          indirect: link.indirect,
          isRecursive: link.isRecursive,
          recursive: link.recursive,
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
      label: relation == "unionNode" ? "Union" : "Minus",
      source: node1.id,
      target: node2.id,
      selected: false,
      suggested: false,
      directed: false,
      indirect: false,
      isRecursive: false,
      recursive: false,
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
    if (this.currentSelected.type == "unionNode") {
      this.insertSuggestion(this.currentSelected, this.getLargestSpecialNodeGroupId(this.currentSelected) + 1)
    } else {
      this.insertSuggestion(this.currentSelected)
    }
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
    if (this.currentSelected.type == "unionNode") {
      this.insertSuggestion(this.currentSelected, this.getLargestSpecialNodeGroupId(this.currentSelected) + 1)
    } else {
      this.insertSuggestion(this.currentSelected)
    }
    this.updateGraphState()
  }

  // Filter Faldo --------------------------
  handleFilterFaldo (event) {
    // Toggle filter

    this.showFaldo = !this.showFaldo
    // Reset suggestion
    this.removeAllSuggestion()
    if (this.currentSelected.type == "unionNode") {
      this.insertSuggestion(this.currentSelected, this.getLargestSpecialNodeGroupId(this.currentSelected) + 1)
    } else {
      this.insertSuggestion(this.currentSelected)
    }
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

  toggleExclude (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.exclude = !attr.exclude
        if (attr.exclude) {
          attr.visible = true
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

  toggleFormAttribute (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.form = !attr.form
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

  handleLinkedNegative (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.linkedNegative = event.target.value == '=' ? false : true
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

  handleLinkedFilterValue (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.linkedFilterValue = event.target.value
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

  handleLinkedNumericSign (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.linkedFilters.map((filter, index) => {
          if (index == event.target.dataset.index) {
            filter.filterSign = event.target.value
          }
        })
      }
    })
    this.updateGraphState()
  }

  toggleAddNumLinkedFilter (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.linkedFilters.push({
          filterValue: "",
          filterSign: "=",
          filterModifier: "+"
        })
      }
    })
    this.updateGraphState()
  }

  toggleRemoveNumLinkedFilter (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.linkedFilters.pop()
      }
    })
    this.updateGraphState()
  }

  handleLinkedNumericModifierSign (event) {
    if (!isNaN(event.target.value)) {
      this.graphState.attr.map(attr => {
        if (attr.id == event.target.id) {
          attr.linkedFilters.map((filter, index) => {
            if (index == event.target.dataset.index) {
              filter.filterModifier = event.target.value
            }
          })
        }
      })
      this.updateGraphState()
    }
  }

  handleLinkedNumericValue (event) {
    if (!isNaN(event.target.value)) {
      this.graphState.attr.map(attr => {
        if (attr.id == event.target.id) {
          attr.linkedFilters.map((filter, index) => {
            if (index == event.target.dataset.index) {
              filter.filterValue = event.target.value
            }
          })
        }
      })
      this.updateGraphState()
    }
  }

  handleDateFilter (event) {
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

  toggleAddDateFilter (event) {
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.filters.push({
          filterValue: null,
          filterSign: "="
        })
      }
    })
    this.updateGraphState()
  }

  // This is a pain, but JS will auto convert time to UTC
  // And datepicker use the local timezone
  // So without this, the day sent will be wrong
  fixTimezoneOffset (date){
    if(!date){return null};
    return new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
  }

  handleFilterDateValue (event) {
    if (!isNaN(event.target.value)) {
      this.graphState.attr.map(attr => {
        if (attr.id == event.target.id) {
          attr.filters.map((filter, index) => {
            if (index == event.target.dataset.index) {
              filter.filterValue = this.fixTimezoneOffset(event.target.value)
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
          attr.linkedFilters = [{
            filterValue: "",
            filterSign: "=",
            filterModifier: "+"
          }]
        }
      }
    })
    this.updateGraphState()
  }

  handleFilterLinked (event){
    if (!isNaN(event.target.value)) {
      this.graphState.attr.map(attr => {
        if (attr.id == event.target.id) {
          attr.linkedFilters.map((filter, index) => {
            if (index == event.target.dataset.index) {
              filter.filterValue = this.fixTimezoneOffset(event.target.value)
            }
          })
        }
      })
      this.updateGraphState()
    }
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

        if (event.target.value != "distance_from"){
          link.faldoFilters = this.defaultFaldoFilters
        }
        if (event.target.value == 'included_in'){
          link.label = "Included in"
        } else if (event.target.value == 'overlap_with'){
          link.label = "Overlap with"
        } else {
          link.label = "Distant from"
        }
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

  // Ontology link methods -----------------------------

  handleRecursiveOntology (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.recursive = event.target.checked
      }
    })
    this.updateGraphState()
  }

  // Faldo filters -----------------------------

  toggleAddFaldoFilter (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.faldoFilters.push({
          filterValue: null,
          filterSign: "=",
          filterModifier: "+",
          filterStart: "start",
          filterEnd: "start"
        })
      }
    })
    this.updateGraphState()
  }

  toggleRemoveFaldoFilter (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.faldoFilters.pop()
      }
    })
    this.updateGraphState()
  }

  handleFaldoModifierSign (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.faldoFilters.map((filter, index) => {
          if (index == event.target.dataset.index) {
            filter.filterModifier = event.target.value
          }
        })
      }
    })
    this.updateGraphState()
  }

  handleFaldoFilterSign (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.faldoFilters.map((filter, index) => {
          if (index == event.target.dataset.index) {
            filter.filterSign = event.target.value
          }
        })
      }
    })
    this.updateGraphState()
  }

  handleFaldoFilterStart (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.faldoFilters.map((filter, index) => {
          if (index == event.target.dataset.index) {
            filter.filterStart = event.target.value
          }
        })
      }
    })
    this.updateGraphState()
  }

  handleFaldoFilterEnd (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.faldoFilters.map((filter, index) => {
          if (index == event.target.dataset.index) {
            filter.filterEnd = event.target.value
          }
        })
      }
    })
    this.updateGraphState()
  }

  handleFaldoValue (event) {
    this.graphState.links.map(link => {
      if (link.id == event.target.id) {
        link.faldoFilters.map((filter, index) => {
          if (index == event.target.dataset.index) {
            filter.filterValue = event.target.value
          }
        })
      }
    })
    this.updateGraphState()
  }

  // Fix update graphState
  fixGraphState() {
    // Fix faldoFilters
    this.graphState.links.map(link => {
      if (!link.faldoFilters) {
        link.faldoFilters = this.defaultFaldoFilters
      }
      if (!link.indirect){
        link.indirect = false
      }
    })
    this.graphState.nodes.map(node => {
      if (!node.depth) {
        if(node.specialNodeId){
          node.legacyBlock = true
        }
        node.depth = []
      }
    })
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
            console.log(this.props.location.state.graphState)
            // redo a query
            this.graphState = this.props.location.state.graphState
            this.initId()
            this.fixGraphState()
            this.setCurrentSelected()
            if (this.currentSelected) {
              if (this.currentSelected.type != "link" && this.currentSelected.type != "posLink" && this.currentSelected.type != "ontoLink") {
                if (this.currentSelected.type == "unionNode") {
                  this.insertSuggestion(this.currentSelected, this.getLargestSpecialNodeGroupId(this.currentSelected) + 1)
                } else {
                  this.insertSuggestion(this.currentSelected)
                }
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
    let isOnto
    let linkView
    let previewButton
    let overviewButton
    let faldoButton
    let launchQueryButton
    let removeButton
    let graphFilters
    let tooltips = (
        <div>
        <Tooltip anchorSelect=".formTooltip" place="top" effect="solid">Mark attribute as a <i>form</i> attribute</Tooltip>
        <Tooltip anchorSelect=".linkTooltip">Link this attribute to another</Tooltip>
        <Tooltip anchorSelect=".optionalTooltip">Show all values, including empty values.</Tooltip>
        <Tooltip anchorSelect=".excludeTooltip">Exclude categories, instead of including</Tooltip>
        <Tooltip anchorSelect=".visibleTooltip">Display attribute value in the results</Tooltip>
        <Tooltip anchorSelect=".linkedTooltip">Regex value, with $1 as a placeholder for the linked value. Ex: $1-suffix</Tooltip>
        </div>
    )

    if (!this.state.waiting) {
      // attribute boxes (right view) only for node
      if (this.currentSelected) {
        isOnto = this.isOntoNode(this.currentSelected.id)
        AttributeBoxes = this.state.graphState.attr.map(attribute => {
          if (attribute.nodeId == this.currentSelected.id && this.currentSelected.type == "node") {
            return (
              <AttributeBox
                key={attribute.id}
                attribute={attribute}
                graph={this.state.graphState}
                handleChangeLink={p => this.handleChangeLink(p)}
                toggleVisibility={p => this.toggleVisibility(p)}
                toggleExclude={p => this.toggleExclude(p)}
                handleNegative={p => this.handleNegative(p)}
                toggleOptional={p => this.toggleOptional(p)}
                toggleFormAttribute={p => this.toggleFormAttribute(p)}
                handleFilterType={p => this.handleFilterType(p)}
                handleFilterValue={p => this.handleFilterValue(p)}
                handleFilterCategory={p => this.handleFilterCategory(p)}
                handleFilterNumericSign={p => this.handleFilterNumericSign(p)}
                handleFilterNumericValue={p => this.handleFilterNumericValue(p)}
                toggleLinkAttribute={p => this.toggleLinkAttribute(p)}
                toggleAddNumFilter={p => this.toggleAddNumFilter(p)}
                toggleAddDateFilter={p => this.toggleAddDateFilter(p)}
                handleFilterDateValue={p => this.handleFilterDateValue(p)}
                handleDateFilter={p => this.handleDateFilter(p)}
                handleLinkedNumericModifierSign={p => this.handleLinkedNumericModifierSign(p)}
                handleLinkedNumericSign={p => this.handleLinkedNumericSign(p)}
                handleLinkedNumericValue={p => this.handleLinkedNumericValue(p)}
                toggleAddNumLinkedFilter={p => this.toggleAddNumLinkedFilter(p)}
                toggleRemoveNumLinkedFilter={p => this.toggleRemoveNumLinkedFilter(p)}
                handleLinkedNegative={p => this.handleLinkedNegative(p)}
                handleLinkedFilterValue={p => this.handleLinkedFilterValue(p)}
                config={this.state.config}
                isOnto={isOnto}
                entityUri={this.currentSelected.uri}
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
            nodesHaveRefs={p => this.nodesHaveRefs(p)}
            nodesHaveStrands={p => this.nodesHaveStrands(p)}
            toggleAddFaldoFilter={p => this.toggleAddFaldoFilter(p)}
            toggleRemoveFaldoFilter={p => this.toggleRemoveFaldoFilter(p)}
            handleFaldoModifierSign={p => this.handleFaldoModifierSign(p)}
            handleFaldoFilterSign={p => this.handleFaldoFilterSign(p)}
            handleFaldoFilterStart={p => this.handleFaldoFilterStart(p)}
            handleFaldoFilterEnd={p => this.handleFaldoFilterEnd(p)}
            handleFaldoValue={p => this.handleFaldoValue(p)}
          />
        }

        if (this.currentSelected.type == "ontoLink") {

          let link = Object.assign(this.currentSelected)
          this.state.graphState.nodes.map(node => {
            if (node.id == this.currentSelected.target) {
              link.target = node
            }
            if (node.id == this.currentSelected.source) {
              link.source = node
            }
          })

          linkView = <OntoLinkView
            link={link}
            handleRecursiveOntology={p => this.handleRecursiveOntology(p)}
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
      overviewButton = (<OverviewModal divHeight={this.divHeight} graphState={this.state.graphState} handleNodeSelection={p => this.handleNodeSelection(p)} handleLinkSelection={p => this.handleLinkSelection(p)}/>)

      let previewIcon = <i className={"fas fa-" + this.state.previewIcon}></i>
      if (this.state.previewIcon == "spinner") {
        previewIcon = <Spinner size="sm" color="light" />
      }
      previewButton = <Button onClick={this.handlePreview} color="secondary" disabled={this.state.disablePreview}>{previewIcon} Run & preview</Button>
      if (this.state.config.logged || this.state.config.anonymousQuery) {
        launchQueryButton = <Button onClick={this.handleQuery} color="secondary" disabled={this.state.disableSave || this.state.exceededQuota}><i className={"fas fa-" + this.state.saveIcon}></i> Run & save</Button>
      }
      if (this.currentSelected != null) {
        removeButton = (
          <ButtonGroup>
            <Button disabled={this.currentSelected.id == 1 ? true : false} onClick={this.handleRemoveNode} color="secondary" size="sm">Remove {this.currentSelected.type == "link" ? "Link" : "Node"}</Button>
          </ButtonGroup>
        )
      }

      faldoButton = (
        <div>
            <CustomInput type="switch" id="filterFaldo" onChange={this.handleFilterFaldo} checked={this.showFaldo} value={this.showFaldo} label="Show FALDO relations"  />
        </div>
      )

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
        <Row className="align-items-center">
          <Col xs="7">
            {graphFilters}
          </Col>
          <Col xs="3">
            {faldoButton}
          </Col>
          <Col xs="2">
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
              {tooltips}
            </div>
          </Col>
        </Row>
        {warningDiskSpace}
        <Row>
          <Col xs="7" style={{ paddingRight: 0 }}>
            <ButtonToolbar className="justify-content-between">
              <ButtonGroup>
                {previewButton}
                {launchQueryButton}
              </ButtonGroup>
              <ButtonGroup>
                {overviewButton}
              </ButtonGroup>
            </ButtonToolbar>
          </Col>
        </Row>
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
