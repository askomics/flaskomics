import React, { Component } from "react"
import axios from 'axios'
import { Alert, Button } from 'reactstrap';
import { Redirect} from 'react-router-dom'
import ErrorDiv from "../error/error"
import WaitingDiv from "../../components/waiting"

import brace from 'brace';
import AceEditor from 'react-ace';

import 'brace/mode/sparql';
import 'brace/theme/tomorrow';

import dedent from "dedent"

import ResultsTable from './resultstable'

export default class Sparql extends Component {

  constructor(props) {
    super(props)
    this.state = {
      logged: this.props.location.state.logged,
      user: this.props.location.state.user,
      results_data: [],
      results_header: [],
      error: false,
      errorMessage: null,
      sparqlInput: this.props.location.state.sparqlQuery
    }
    this.handleCodeChange = this.handleCodeChange.bind(this)
    this.launchQuery = this.launchQuery.bind(this)
  }

  handleCodeChange(code) {
    this.setState({
      sparqlInput: code
    })
  }

  launchQuery() {

    let requestUrl = '/api/sparql/query'
    let data = {
      query: this.state.sparqlInput
    }
    axios.post(requestUrl, data, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
    .then(response => {
      console.log(requestUrl, response.data)
      this.setState({
        results_data: response.data.data,
        results_header: response.data.header,
        waiting: false,
        error: false
      })
    })
    .catch(error => {
      console.log(error, error.response.data.errorMessage)
      this.setState({
        results_data: [],
        results_header: [],
        waiting: false,
        error: true,
        errorMessage: error.response.data.errorMessage,
        status: error.response.status
      })
    })
  }


  render() {

    let resultsTable
    if (this.state.results_header.length > 0) {
      resultsTable = (
        <ResultsTable data={this.state.results_data} header={this.state.results_header} />
      )
    }

    return (
      <div className="container">
        <h2>SPARQL query</h2>
        <hr />
        <br />
        <div>
          <AceEditor
            mode="sparql"
            theme="tomorrow"
            onChange={this.handleCodeChange}
            name="sparqlQuery"
            fontSize={18}
            showPrintMargin={true}
            showGutter={true}
            highlightActiveLine={true}
            value={this.state.sparqlInput}
            editorProps={{$blockScrolling: true}}
            height={400}
            width={"auto"}
          />
        </div>

        <br />
        <Button onClick={this.launchQuery} color="secondary">Launch query</Button>
        <br />
        <br />


        {resultsTable}

        <WaitingDiv waiting={this.state.waiting} center />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}