import React, { Component } from "react"
import axios from 'axios'
import { Alert, Button, InputGroupAddon, Input, InputGroup } from 'reactstrap';
import { Redirect} from 'react-router-dom'
import ResultsFilesTable from './resultsfilestable'
import ErrorDiv from "../error/error"
import WaitingDiv from "../../components/waiting"
import update from 'react-addons-update'
import ResultsTable from '../sparql/resultstable'

export default class Results extends Component {

  constructor(props) {
    super(props)
    this.state = {
      waiting: true,
      error: false,
      errorMessage: null,
      results: [],
      selected: [],
      resultsPreview: [],
      headerPreview: []
    }
    this.cancelRequest
    this.deleteSelectedResults = this.deleteSelectedResults.bind(this)
  }

  isDisabled() {
    return this.state.selected.length == 0 ? true : false
  }

  deleteSelectedResults() {
    let requestUrl = '/api/results/delete'
    let data = {
      filesIdToDelete: this.state.selected
    }
    axios.post(requestUrl, data)
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        files: response.data.files,
        selected: [],
        error: response.data.error,
        errorMessage: response.data.errorMessage
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status,
        selected: []
      })
    })
  }

  componentDidMount() {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/results'
      axios.get(requestUrl, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          results: response.data.files,
          waiting: false
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
  }

  componentWillUnmount() {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }



  render() {

    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

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

    // preview
    let resultsTable
    if (this.state.resultsPreview.length > 0) {
      resultsTable = (
        <div>
          <h4>Result preview</h4>
          <hr />
          <ResultsTable data={this.state.resultsPreview} header={this.state.headerPreview} currentPreview={this.state.currentPreview} />
        </div>
      )
    }

    return (
      <div className="container">
        {redirectLogin}
        <h2>Results</h2>
        <hr />
        <ResultsFilesTable results={this.state.results} setStateResults={p => this.setState(p)} selected={this.state.selected} waiting={this.state.waiting} />
        <Button disabled={this.isDisabled()} onClick={this.deleteSelectedResults} color="danger"><i className="fas fa-trash-alt"></i> Delete</Button>
        <br /><br />
        {resultsTable}
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}