import React, { Component } from "react"
import axios from 'axios'
import BootstrapTable from 'react-bootstrap-table-next'
import { CustomInput, Input, FormGroup, ButtonGroup, Button } from 'reactstrap'
import update from 'react-addons-update'

export default class CsvTable extends Component {

  constructor(props) {
    super(props)
    this.state = {
      name: props.file.name,
      id: props.file.id,
      header: props.file.csv_data.header,
      columns_type: props.file.csv_data.columns_type,
      integrated: false
    }
    this.cancelRequest
    this.headerFormatter = this.headerFormatter.bind(this)
    this.handleChangeType = this.handleChangeType.bind(this)
    this.integrate = this.integrate.bind(this)
  }

  handleChangeType(index, event) {

    this.setState({
      columns_type: this.columns_type.types.map((elem, i) => i == index ? event.target.value : elem)
    })
  }

  headerFormatter(column, colIndex) {

    let boundChangeType = this.handleChangeType.bind(this, colIndex);

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
            <optgroup label="Position attributes">
              <option value="organism" >Organism</option>
              <option value="chromosome" >Chromosome</option>
              <option value="strand" >Strand</option>
              <option value="start" >Start</option>
              <option value="end" >End</option>
            </optgroup>
            <optgroup label="Relation">
              <option value="general_relation" >General</option>
              <option value="symetric_relation" >Symetric</option>
            </optgroup>
            </CustomInput>
          </FormGroup>
      </div>
    )
  }

  integrate(event) {

    let requestUrl = '/api/files/integrate'
    let data = {
      fileId: this.state.id,
      columns_type: this.state.columns_type,
      public: event.target.value == 'public' ? true : false,
      type: 'csv'
    }
    axios.post(requestUrl, data, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
    .then(response => {
      console.log(requestUrl, response.data)
      // this.setState({
      //   files: response.data.files,
      //   waiting: false
      // })
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

  render() {

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

    return (
      <div>
        <h4>{this.state.name}</h4>
        <div className="preview-table-div">
          <BootstrapTable
            wrapperClasses="preview-table"
            bootstrap4
            keyField={this.state.header[0]}
            data={this.props.file.csv_data.content_preview}
            columns={columns}
          />
        </div>
        <br /><br />
        <div className="center-div">
          <ButtonGroup>
            <Button onClick={this.integrate} value="private" color="secondary"><i className="fas fa-lock"></i> Integrate (private dataset)</Button>
            <Button onClick={this.integrate} value="public" color="secondary"><i className="fas fa-globe-europe"></i> Integrate (public dataset)</Button>
          </ButtonGroup>
        </div>
      </div>
    )
  }
}
