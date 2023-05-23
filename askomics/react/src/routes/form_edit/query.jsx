import React, { Component } from 'react'
import axios from 'axios'
import { Alert, Button, Row, Col, ButtonGroup, Input, Spinner } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import { Tooltip } from 'react-tooltip'
import AttributeBox from './attribute'
import Entity from './entity'
import ResultsTable from '../sparql/resultstable'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'

export default class FormEditQuery extends Component {

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
      formId: null,
      resultsPreview: [],
      headerPreview: [],
      waiting: true,
      error: false,
      errorMessage: null,
      saveTick: false,

      // Preview icons
      disableSave: false,
      saveIcon: "play",
    }

    this.graphState = {
      nodes: [],
      links: [],
      attr: []
    }

    this.idNumber = 0
    this.specialNodeIdNumber = 0
    this.previousSelected = null
    this.currentSelected = null
    this.cancelRequest

    this.handleSave = this.handleSave.bind(this)

  }

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

  setEntityName(event){
    this.graphState.attr.map(attr => {
      if (attr.nodeId == event.target.id) {
        attr.entityDisplayLabel = event.target.value
      }
    })
    this.updateGraphState()
  }

  setAttributeName(event){
    this.graphState.attr.map(attr => {
      if (attr.id == event.target.id) {
        attr.displayLabel = event.target.value
      }
    })
    this.updateGraphState()
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

  count_displayed_attributes() {
    return this.graphState.attr.map(attr => {
      return attr.visible ? 1 : 0
    }).reduce((a, b) => a + b)
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
    if (typeUri == "http://www.w3.org/2001/XMLSchema#date") {
      return "date"
    }
  }

  updateGraphState (waiting=this.state.waiting) {
    this.setState({
      graphState: this.graphState,
      previewIcon: "table",
      resultsPreview: [],
      headerPreview: [],
      disableSave: false,
      saveIcon: "play",
      waiting: waiting
    })
  }

  // Preview results and Launch query buttons -------
  handleSave (event) {
    let requestUrl = '/api/results/save_form'
    let data = {
      graphState: this.graphState,
      formId: this.formId
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
      if (! (this.props.location.state.formId && this.props.location.state.graphState)){
        redirectLogin = <Redirect to="/" />
      }

      let requestUrl = '/api/query/abstraction'
      axios.get(requestUrl, { baseURL: this.state.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
        .then(response => {
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
          this.formId = this.props.location.state.formId
          this.graphState = this.props.location.state.graphState
          this.updateGraphState()
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


    let AttributeBoxes
    let Entities = []
    let previewButton
    let entityMap = new Map()
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
      this.state.graphState.attr.forEach(attribute => {
        if (attribute.form) {
          if (! entityMap.has(attribute.nodeId)){
            entityMap.set(attribute.nodeId, {entity_label: attribute.entityDisplayLabel ? attribute.entityDisplayLabel : attribute.entityLabel, attributes:[]})
          }
          entityMap.get(attribute.nodeId).attributes.push(
            <AttributeBox
              attribute={attribute}
              graph={this.state.graphState}
              handleChangeLink={p => this.handleChangeLink(p)}
              toggleVisibility={p => this.toggleVisibility(p)}
              toggleExclude={p => this.toggleExclude(p)}
              handleNegative={p => this.handleNegative(p)}
              toggleOptional={p => this.toggleOptional(p)}
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
              setAttributeName={p => this.setAttributeName(p)}
            />
          )
        }
      })
    }

    entityMap.forEach((value, key) => {
      Entities.push(
        <Entity
          setEntityName={p => this.setEntityName(p)}
          entity_id={key}
          entity={value.entity_label}
          attribute_boxes={value.attributes}
        />
      )
    })

      // buttons


    let saveButton = <Button onClick={this.handleSave} color="secondary" disabled={this.state.disableSave}><i className={"fas fa-" + this.state.saveIcon}></i> Save</Button>

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
        <h2>Form editor</h2>
        <hr />
        <WaitingDiv waiting={this.state.waiting} center />
        <br />
        <Row>
          <Col xs="12">
            <div style={{ display: 'block', 'overflow-y': 'auto' }}>
              {Entities}
              {tooltips}
            </div>
          </Col>
        </Row>
        {warningDiskSpace}
        <br />
        <ButtonGroup>
          {saveButton}
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

FormEditQuery.propTypes = {
  location: PropTypes.object,
  waitForStart: PropTypes.bool
}
