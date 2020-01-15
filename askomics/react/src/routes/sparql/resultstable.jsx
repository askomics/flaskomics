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
    this.utils = new Utils()
  }

  render () {
    let columns = this.props.header.map((colName, index) => {
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
