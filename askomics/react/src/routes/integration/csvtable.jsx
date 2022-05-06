import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import { Collapse, CustomInput, Input, FormGroup, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'
import AdvancedOptions from './advancedoptions'
import Utils from '../../classes/utils'
import ErrorDiv from '../error/error'

export default class CsvTable extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      name: props.file.name,
      id: props.file.id,
      header: props.file.data.header.map(elem => {
        return {name: elem, newName: elem, input: false}
      }),
      columns_type: props.file.data.columns_type,
      integrated: false,
      publicTick: false,
      privateTick: false,
      customUri: "",
      externalEndpoint: "",
      error: false,
      errorMessage: null,
      status: null
    }
    this.cancelRequest
    this.headerFormatter = this.headerFormatter.bind(this)
    this.handleChangeType = this.handleChangeType.bind(this)
    this.integrate = this.integrate.bind(this)
    this.toggleHeaderForm = this.toggleHeaderForm.bind(this)
    this.handleChangeHeader = this.handleChangeHeader.bind(this)
  }

  handleChangeType (index, event) {
    this.setState({
      columns_type: this.state.columns_type.map((elem, i) => i == index ? event.target.value : elem),
      publicTick: false,
      privateTick: false
    })
  }

  confirmUpdateHeader (event) {
    if (event.key === "Enter") {
      // Update column type if a relation is entered
      if (event.target.value.split("@").length == 2) {
        let newType = "general_relation"
        this.setState({
          header: update(this.state.header, { [event.target.id]: {input: { $set: false}}}),
          columns_type: update(this.state.columns_type, { [event.target.id]: { $set: newType }})
        })
      } else {
        this.setState({
          header: update(this.state.header, { [event.target.id]: {input: { $set: false}}})
        })
      }
    }
  }

  headerFormatter (column, colIndex) {
    let boundChangeType = this.handleChangeType.bind(this, colIndex)

    let colInput = <p id={colIndex} onClick={this.toggleHeaderForm}>{this.state.header[colIndex]["newName"]}</p>
    if (this.state.header[colIndex]["input"]) {
      colInput = <Input
        value={this.state.header[colIndex]["newName"]}
        name="header"
        id={colIndex}
        onChange={this.handleChangeHeader}
        onFocus={event => {event.target.select()}}
        autoFocus
        onKeyPress={event => this.confirmUpdateHeader(event)}
      />
    }

    if (colIndex == 0) {
      return (
        <div>
          <FormGroup>
            {colInput}
            <CustomInput type="select" id="typeSelect" name="typeSelect" value={this.state.columns_type[colIndex]} onChange={boundChangeType}>
              <option value="start_entity" >Start entity</option>
              <option value="entity" >Entity</option>
            </CustomInput>
          </FormGroup>
        </div>
      )
    }

    if (colIndex == 1) {
      return (
        <div>
          <FormGroup>
            {colInput}
            <CustomInput type="select" id="typeSelect" name="typeSelect" value={this.state.columns_type[colIndex]} onChange={boundChangeType}>
              <optgroup label="Properties">
                <option value="label" >Entity label</option>
              </optgroup>
              <optgroup label="Attributes">
                <option value="numeric" >Numeric</option>
                <option value="text" >Text</option>
                <option value="category" >Category</option>
                <option value="boolean" >Boolean</option>
                <option value="date" >Date</option>
              </optgroup>
              <optgroup label="Faldo attributes">
                <option value="reference" >Reference</option>
                <option value="strand" >Strand</option>
                <option value="start" >Start</option>
                <option value="end" >End</option>
              </optgroup>
              <optgroup label="Relation">
                <option value="general_relation" >Directed</option>
                <option value="symetric_relation" >Symetric</option>
              </optgroup>
            </CustomInput>
          </FormGroup>
        </div>
      )
    }

    return (
      <div>
        <FormGroup>
          {colInput}
          <CustomInput type="select" id="typeSelect" name="typeSelect" value={this.state.columns_type[colIndex]} onChange={boundChangeType}>
            <optgroup label="Attributes">
              <option value="numeric" >Numeric</option>
              <option value="text" >Text</option>
              <option value="category" >Category</option>
              <option value="boolean" >Boolean</option>
              <option value="date" >Date</option>
            </optgroup>
            <optgroup label="Faldo attributes">
              <option value="reference" >Reference</option>
              <option value="strand" >Strand</option>
              <option value="start" >Start</option>
              <option value="end" >End</option>
            </optgroup>
            <optgroup label="Relation">
              <option value="general_relation" >Directed</option>
              <option value="symetric_relation" >Symetric</option>
            </optgroup>
          </CustomInput>
        </FormGroup>
      </div>
    )
  }

  integrate (event) {
    let requestUrl = '/api/files/integrate'
    let tick = event.target.value == 'public' ? 'publicTick' : 'privateTick'
    let data = {
      fileId: this.state.id,
      columns_type: this.state.columns_type,
      header_names: this.state.header.map(header => {
        return header.newName
      }),
      public: event.target.value == 'public',
      type: 'csv',
      customUri: this.state.customUri,
      externalEndpoint: this.state.externalEndpoint
    }
    axios.post(requestUrl, data, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          [tick]: true
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
      })
  }

  handleChangeUri (event) {
    this.setState({
      customUri: event.target.value,
      publicTick: false,
      privateTick: false
    })
  }

  handleChangeEndpoint (event) {
    this.setState({
      externalEndpoint: event.target.value,
      publicTick: false,
      privateTick: false
    })
  }

  toggleHeaderForm(event) {
    this.setState({
      header: update(this.state.header, { [event.target.id]: { input: { $set: true } } })
    })
  }

  handleChangeHeader(event) {
    this.setState({
      header: update(this.state.header, { [event.target.id]: { newName: { $set: event.target.value } } })
    })

  }

  render () {
    let columns = this.state.header.map((colName, index) => {
      return ({
        dataField: this.state.header[index]["name"],
        text: this.state.header[index]["name"],
        sort: false,
        headerFormatter: this.headerFormatter,
        index: index,
        selectedType: this.state.columns_type[index],
        formatter: (cell, row) => {
          let text = row[this.state.header[index]["name"]]
          if (this.utils.isUrl(text)) {
            return <a href={text} target="_blank" rel="noreferrer">{this.utils.truncate(this.utils.splitUrl(text), 25)}</a>
          } else {
            return this.utils.truncate(text, 25)
          }
        },
      })
    })

    let privateIcon = <i className="fas fa-lock"></i>
    if (this.state.privateTick) {
      privateIcon = <i className="fas fa-check text-success"></i>
    }
    let publicIcon = <i className="fas fa-globe-europe"></i>
    if (this.state.publicTick) {
      publicIcon = <i className="fas fa-check text-success"></i>
    }
    let privateButton
    if (this.props.config.user.admin || !this.props.config.singleTenant){
        privateButton = <Button onClick={this.integrate} value="private" color="secondary" disabled={this.state.privateTick}>{privateIcon} Integrate (private dataset)</Button>
    }
    let publicButton
    if (this.props.config.user.admin) {
      publicButton = <Button onClick={this.integrate} value="public" color="secondary" disabled={this.state.publicTick}>{publicIcon} Integrate (public dataset)</Button>
    }

    let body

    if (this.props.file.error) {
      body = (
        <ErrorDiv status={500} error={this.props.file.error} errorMessage={this.props.file.error_message} />
      )
    } else {
      body = (
        <div>
          <div className="asko-table-div">
            <BootstrapTable
              classes="asko-table"
              wrapperClasses="asko-table-wrapper"
              bootstrap4
              keyField={this.state.header[0]["name"]}
              data={this.props.file.data.content_preview}
              columns={columns}
            />
          </div>
          <br />
          <AdvancedOptions
            config={this.props.config}
            hideDistantEndpoint={true}
            handleChangeUri={p => this.handleChangeUri(p)}
            handleChangeEndpoint={p => this.handleChangeEndpoint(p)}
            customUri={this.state.customUri}
          />
          <br />
          <div className="center-div">
            <ButtonGroup>
              {privateButton}
              {publicButton}
            </ButtonGroup>
          </div>
        </div>
      )
    }

    return (
      <div>
        <h4>{this.state.name} (preview)</h4>
        {body}
        {this.state.error ? <br /> : ''}
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}

CsvTable.propTypes = {
  file: PropTypes.object,
  config: PropTypes.object
}
