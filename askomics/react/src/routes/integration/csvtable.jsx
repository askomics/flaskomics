import React, { Component } from "react"
import BootstrapTable from 'react-bootstrap-table-next'
import { CustomInput, Input, FormGroup } from 'reactstrap'
import update from 'react-addons-update'

export default class CsvTable extends Component {

  constructor(props) {
    super(props)
    this.state = {
      name: props.file.name,
      header: props.file.header,
      types: props.file.columns_type,
      integrated: false
    }
    this.headerFormatter = this.headerFormatter.bind(this)
    this.handleChangeType = this.handleChangeType.bind(this)
  }

  handleChangeType(index, event) {
    this.setState({
      types: this.state.types.map((elem, i) => i == index ? event.target.value : elem)
    })
  }

  headerFormatter(column, colIndex) {

    let boundChangeType = this.handleChangeType.bind(this, colIndex);

    if (colIndex == 0) {
      return (
      <div>
        <FormGroup>
            <p>{this.state.header[colIndex]}</p>
            <CustomInput type="select" id="typeSelect" name="typeSelect" value={this.state.types[colIndex]} onChange={boundChangeType}>
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
            <CustomInput type="select" id="typeSelect" name="typeSelect" value={this.state.types[colIndex]} onChange={boundChangeType}>
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


  render() {

    let columns = this.state.header.map((colName, index) => {
      return ({
        dataField: this.state.header[index],
        text: this.state.header[index],
        sort: false,
        headerFormatter: this.headerFormatter,
        index: index,
        selectedType: this.state.types[index]
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
            data={this.props.file.preview}
            columns={columns}
          />
        </div>
        <br />
      </div>
    )
  }
}
