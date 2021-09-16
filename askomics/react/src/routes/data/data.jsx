import React, { Component } from 'react'
import axios from 'axios'
import { Button, Form, FormGroup, Label, Input, Alert, Row, Col, CustomInput } from 'reactstrap'
import BootstrapTable from 'react-bootstrap-table-next'
import paginationFactory from 'react-bootstrap-table2-paginator'
import cellEditFactory from 'react-bootstrap-table2-editor'
import update from 'react-addons-update'
import { withRouter } from "react-router-dom";
import PropTypes from 'prop-types'
import Utils from '../../classes/utils'
import { Redirect } from 'react-router-dom'
import WaitingDiv from '../../components/waiting'
import ErrorDiv from '../error/error'

class Data extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      isLoading: true,
      error: false,
      errorMessage: '',
      data: [],
    }
  }

  componentDidMount () {
    if (!this.props.waitForStart) {
      this.loadData()
    }
  }

  loadData() {
    let uri = this.props.match.params.uri;
    let requestUrl = '/api/data/' + uri
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          isLoading: false,
          data: response.data.data,
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          success: !error.response.data.error
        })
      })
  }

  componentWillUnmount () {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  render () {
    let uri = this.props.match.params.uri;

    let columns = [{
      dataField: 'predicat',
      text: 'Property',
      sort: true,
      formatter: (cell, row) => {
        if (this.utils.isUrl(cell)) {
          return this.utils.splitUrl(cell)
        }
        return cell
      }
    },{
      dataField: 'object',
      text: 'Value',
      sort: true,
      formatter: (cell, row) => {
        if (this.utils.isUrl(cell)) {
          if (cell.startsWith(this.props.config.namespaceInternal)){
            return this.utils.splitUrl(cell)
          } else {
            return <a href={cell} target="_blank" rel="noreferrer">{this.utils.splitUrl(cell)}</a>
          }
        }
        return cell
      }
    }]


    return (
      <div className="container">
        <h2>Information about uri {uri}</h2>
        <br />
        <div className="asko-table-height-div">
          <BootstrapTable
            classes="asko-table"
            wrapperClasses="asko-table-wrapper"
            tabIndexCell
            bootstrap4
            keyField='id'
            data={this.state.data}
            columns={columns}
            pagination={paginationFactory()}
            noDataIndication={'No results for this URI. You may not have access to any graph including it.'}
          />
        </div>
      </div>
    )
  }
}

Data.propTypes = {
  waitForStart: PropTypes.bool,
  config: PropTypes.object,
  match: PropTypes.object
}

export default withRouter(Data)
