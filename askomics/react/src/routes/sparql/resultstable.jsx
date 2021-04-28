import React, { Component } from 'react'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import WaitingDiv from '../../components/waiting'
import { Badge } from 'reactstrap'
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'

export default class ResultsTable extends Component {
  constructor (props) {
    super(props)
    this.state = {
        filter_columns: {}
    }
    this.utils = new Utils()
    this.custom_compare = this.custom_compare.bind(this)
  }

  custom_compare(a, b, column_name){
    let result, num_a, num_b;
    if (typeof b === 'string') {
      if (this.state.filter_columns[column_name]){
        num_a = Number(a)
        num_b = Number(b)
        if (Number.isNaN(num_a) || Number.isNaN(num_b)){
          this.state.filter_columns[column_name] = false
          result = b.localeCompare(a);
        } else {
          result = num_a > num_b ? -1 : ((num_a < num_b) ? 1 : 0);
        }
      } else {
        result = b.localeCompare(a);
      }
    } else {
      result = a > b ? -1 : ((a < b) ? 1 : 0);
    }
    return result;
  }

  render () {
    let columns = this.props.header.map((colName, index) => {
      this.state.filter_columns[colName] = true;
      return ({
        dataField: colName,
        text: colName,
        sort: true,
        index: index,
        formatter: (cell, row) => {
          if (this.utils.isUrl(cell)) {
            return <a href={cell}>{this.utils.splitUrl(cell)}</a>
          }
          return cell
        },
        sortFunc: (a, b, order, dataField, rowA, rowB) => {
          if (order === 'asc') {
            return this.custom_compare(a,b, dataField);
          }
          return this.custom_compare(b,a, dataField); // desc
        }
      })
    })

    return (
      <div>
        <div className="asko-table-height-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            tabIndexCell
            bootstrap4
            keyField='id'
            data={this.props.data}
            columns={columns}
            pagination={paginationFactory()}
            noDataIndication={'No results'}
          />
        </div>
      </div>
    )
  }
}

ResultsTable.propTypes = {
  header: PropTypes.object,
  data: PropTypes.object,
}
