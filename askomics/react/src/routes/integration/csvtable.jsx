import React, { Component } from "react"
import BootstrapTable from 'react-bootstrap-table-next'

export default class CsvTable extends Component {


  constructor(props) {
    super(props)
  }


  render() {

    let columns = this.props.file.header.map(colName => {
      return ({
        dataField: colName,
        text: colName,
        sort: false
      })
    })

    console.log('columns', columns)

    return (
      <div>
        <h4>{this.props.file.name}</h4>
        <div className="preview-table-div">
          <BootstrapTable
            wrapperClasses="preview-table"
            bootstrap4
            keyField='id'
            data={this.props.file.preview}
            columns={columns}
          />
        </div>
        <br />
      </div>
    )
  }
}
