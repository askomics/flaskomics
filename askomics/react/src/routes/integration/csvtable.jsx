import React, { Component } from 'react'
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import { CustomInput, Input, FormGroup, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'
import PropTypes from 'prop-types'

export default class CsvTable extends Component {
  constructor (props) {
    super(props)
    this.state = {
      name: props.file.name,
      id: props.file.id,
      header: props.file.data.header,
      columns_type: props.file.data.columns_type,
      integrated: false,
      publicTick: false,
      privateTick: false
    }
    this.cancelRequest
    this.headerFormatter = this.headerFormatter.bind(this)
    this.handleChangeType = this.handleChangeType.bind(this)
    this.integrate = this.integrate.bind(this)
  }

  handleChangeType (index, event) {
    this.setState({
      columns_type: this.state.columns_type.map((elem, i) => i == index ? event.target.value : elem),
      publicTick: false,
      privateTick: false
    })
  }

  headerFormatter (column, colIndex) {
    let boundChangeType = this.handleChangeType.bind(this, colIndex)

    if (colIndex == 0) {
      return (
        <div>
          <FormGroup>
            <p>{this.state.header[colIndex]}</p>
            <CustomInput type="select" id="typeSelect" name="typeSelect" value={this.state.columns_type[colIndex]} onChange={boundChangeType}>
              <option value="start_entity" >Start entity</option>
              <option value="entity" >Entity</option>
            </CustomInput>
          </FormGroup>
        </div>
      )
    }

    return (
      <div>
        <FormGroup>
          <p>{this.state.header[colIndex]}</p>
          <CustomInput type="select" id="typeSelect" name="typeSelect" value={this.state.columns_type[colIndex]} onChange={boundChangeType}>
            <optgroup label="Attributes">
              <option value="numeric" >Numeric</option>
              <option value="text" >Text</option>
              <option value="category" >Category</option>
              <option value="datetime" >Datetime</option>
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
      public: event.target.value == 'public',
      type: 'csv'
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

  render () {
    let columns = this.state.header.map((colName, index) => {
      return ({
        dataField: this.state.header[index],
        text: this.state.header[index],
        sort: false,
        headerFormatter: this.headerFormatter,
        index: index,
        selectedType: this.state.columns_type[index]
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

    let publicButton
    if (this.props.config.user.admin) {
      publicButton = <Button onClick={this.integrate} value="public" color="secondary" disabled={this.state.publicTick}>{publicIcon} Integrate (public dataset)</Button>
    }

    return (
      <div>
        <h4>{this.state.name} (preview)</h4>
        <div className="asko-table-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            bootstrap4
            keyField={this.state.header[0]}
            data={this.props.file.data.content_preview}
            columns={columns}
          />
        </div>
        <br /><br />
        <div className="center-div">
          <ButtonGroup>
            <Button onClick={this.integrate} value="private" color="secondary" disabled={this.state.privateTick}>{privateIcon} Integrate (private dataset)</Button>
            {publicButton}
          </ButtonGroup>
        </div>
      </div>
    )
  }
}

CsvTable.propTypes = {
  file: PropTypes.object,
  config: PropTypes.object
}
