import React, { Component } from "react"
import axios from 'axios'
import { Alert, Button } from 'reactstrap';
import { Redirect} from 'react-router-dom'
import ErrorDiv from "../error/error"
import WaitingDiv from "../../components/waiting"
import update from 'react-addons-update'
import Visualization from './visualization'

export default class Query extends Component {

  constructor(props) {
    super(props)
    this.state = {
      logged: this.props.location.state.logged,
      user: this.props.location.state.user,
      startpoint: this.props.location.state.startpoint,
      abstraction: [],
      graphState: {
        nodes: [],
        links: []
      },
      waiting: true,
      error: false,
      errorMessage: null,
    }
    this.cancelRequest
  }

  componentDidMount() {
    if (!this.props.waitForStart) {
      let requestUrl = '/api/startpoints/abstraction'
      axios.get(requestUrl, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          waiting: false,
          abstraction: response.data.abstraction,
          graphState: {
            nodes: [
              {
                uri: this.state.startpoint,
                label: response.data.abstraction.reduce(node => {
                  if (node.uri == this.state.startpoint) {
                    return node.label
                  }
                }),
                val: 1,
                selected: true
              }
            ],
            links: []
          }
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

    return (
      <div className="container">
        {redirectLogin}
        <h2>Query Builder</h2>
        <hr />
        <WaitingDiv waiting={this.state.waiting} center />
        <Visualization
          abstraction={this.state.abstraction}
          startpoint={this.state.startpoint}
          graphState={this.state.graphState}
          logged={this.state.logged}
          user={this.state.user}
          waiting={this.state.waiting}
          setStateAsk={p => this.setState(p)}
        />
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}