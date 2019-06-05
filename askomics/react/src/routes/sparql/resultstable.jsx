import React, { Component } from 'react'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import WaitingDiv from '../../components/waiting'
import { Badge } from 'reactstrap'
import PropTypes from 'prop-types'

export default class ResultsTable extends Component {
  constructor (props) {
    super(props)
  }

  isUrl (str) {
    var pattern = new RegExp('^(https?:\\/\\/)?' + // protocol
      '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
      '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
      '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
      '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
      '(\\#[;&a-z\\d%_.~+=-]*)?$', 'i') // fragment locator
    return !!pattern.test(str)
  }

  render () {
    let columns = this.props.header.map((colName, index) => {
      return ({
        dataField: colName,
        text: colName,
        sort: true,
        index: index,
        formatter: (cell, row) => {
          if (this.isUrl(cell)) {
            return <a href={cell}>{cell.split('#')[1]}</a>
          }
          return cell
        }
      })
    })

    return (
      <div>
        <div className="asko-table-div">
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
