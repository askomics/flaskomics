import React, { Component } from "react"
import axios from 'axios'
import { Alert, Button } from 'reactstrap';
import { Redirect} from 'react-router-dom'
import ErrorDiv from "../error/error"
import WaitingDiv from "../../components/waiting"
import update from 'react-addons-update'

export default class Ask extends Component {

  constructor(props) {
    super(props)
    this.state = {
      waiting: true,
      error: false,
      errorMessage: null,
      startpoints: [],
      selected: null,
      startSession: false
    }
    this.cancelRequest
    this.handleClick = this.handleClick.bind(this)
    this.handleStart = this.handleStart.bind(this)
  }

  componentDidMount() {

    if (!this.props.waitForStart) {
      let requestUrl = '/api/startpoints'
      axios.get(requestUrl, {cancelToken: new axios.CancelToken((c) => {this.cancelRequest = c})})
      .then(response => {
        console.log(requestUrl, response.data)
        this.setState({
          waiting: false,
          startpoints: response.data.startpoints.map(startpoint => new Object({
            graphs: startpoint.graphs,
            entity: startpoint.entity,
            entity_label: startpoint.entity_label,
            public: startpoint.public,
            private: startpoint.private,
            selected: false
          }))
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          waiting: false,
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status
        })
      })
    }
  }

  componentWillUnmount() {
    if (!this.props.waitForStart) {
      this.cancelRequest()
    }
  }

  handleClick(event) {
    this.setState({
      selected: event.target.id
    })
  }

  handleStart(event) {
    console.log("Start session with " + this.state.selected)
    this.setState({
      startSession: true
    })
  }

  disabledStartButton() {
    return this.state.selected ? false : true
  }


  render() {

    let redirectLogin
    if (this.state.status == 401) {
      redirectLogin = <Redirect to="/login" />
    }

    let redirectQueryBuilder
    if (this.state.startSession) {
      redirectQueryBuilder = <Redirect to={{
        pathname: "/query",
        state: {
          startpoint: this.state.selected,
          user: this.props.user,
          logged: this.props.logged
        }
      }} />
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

    let startpoints
    if (!this.state.waiting) {
      startpoints = (
        <div>
          <p>Select an entity to start a session:</p>
          <div className="startpoints-div">
            {this.state.startpoints.map(startpoint => (
              <div className="input-label" id={startpoint.entity_label}>
                <input className="startpoint-radio" value={startpoint.entity_label} type="radio" name="startpoints" id={startpoint.entity} onClick={this.handleClick}></input>
                <label className="startpoint-label" id={startpoint.name} htmlFor={startpoint.entity}>
                  {startpoint.public ? <i className="fa fa-globe-europe text-info"></i> : <nodiv></nodiv> } <nodiv> </nodiv>
                  {startpoint.private ? <i className="fa fa-lock text-primary"></i> : <nodiv></nodiv> }
                  <em> {startpoint.entity_label}</em>
                </label>
              </div>
            ))}
          </div>
          <br />
          <Button disabled={this.disabledStartButton()} onClick={this.handleStart} color="secondary">Start!</Button>
        </div>
      )
    }

    return (
      <div className="container">
        {redirectQueryBuilder}
        {redirectLogin}
        <h2>Ask!</h2>
        <hr />
        <WaitingDiv waiting={this.state.waiting} center />
        {startpoints}
        <ErrorDiv status={this.state.status} error={this.state.error} errorMessage={this.state.errorMessage} />
      </div>
    )
  }
}