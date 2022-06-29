import React, { Component} from 'react'
import axios from 'axios'
import PropTypes from 'prop-types'
import { Input } from 'reactstrap'
import Autosuggest from 'react-autosuggest';


export default class Autocomplete extends Component {
  constructor (props) {
    super(props)
    this.state = {
        ontologyShort: this.getAutoComplete(),
        maxResults: this.props.config.autocompleteMaxResults,
        options: []
    }

    this.handleFilterValue = this.props.handleFilterValue.bind(this)
    this.autocompleteOntology = this.autocompleteOntology.bind(this)
    this.onSuggestionsFetchRequested = this.onSuggestionsFetchRequested.bind(this)
    this.onSuggestionsClearRequested = this.onSuggestionsClearRequested.bind(this)
    this.cancelRequest
    this.handleOntoValue = this.handleOntoValue.bind(this)
    this.WAIT_INTERVAL = 500
    this.timerID
  }

  getAutoComplete () {
      let selectedOnto =  this.props.config.ontologies.find(onto => onto.uri == this.props.entityUri)
      if (selectedOnto){
        return selectedOnto.short_name
      }
      return ""
  }

  autocompleteOntology (value) {
    if (this.state.ontologyShort.length == 0){ return }

    let userInput = value
    let requestUrl = '/api/ontology/' + this.state.ontologyShort + "/autocomplete"

    if (value.length < 3) { return }

    axios.get(requestUrl, {baseURL: this.props.config.proxyPath, params:{q: userInput}, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        this.setState({
          options: response.data.results
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


  handleOntoValue (event, value) {
    this.handleFilterValue({target:{value: value.newValue, id: this.props.attributeId}})
  }


  renderSuggestion (suggestion, {query, isHighlighted}) {
    let textArray = suggestion.split(RegExp(query, "gi"));
    let match = suggestion.match(RegExp(query, "gi"));

    return (
      <span>
        {textArray.map((item, index) => (
          <span key={index}>
            {item}
            {index !== textArray.length - 1 && match && (
              <b>{match[index]}</b>
            )}
          </span>
        ))}
      </span>
    );
  }

  onSuggestionsClearRequested () {
    this.setState({
          options: []
    })
  }

  getSuggestionValue (suggestion) { 
    return suggestion
  };

  onSuggestionsFetchRequested ( value ){
    clearTimeout(this.timerID)
    this.timerID = setTimeout(() => {
        this.autocompleteOntology(value.value)
    }, this.WAIT_INTERVAL)
  };
  

  renderInputComponent (inputProps){
    return(
        <div>
            <Input type="text" {...inputProps} />
        </div>
    )
  }


  shouldRenderSuggestions(value, reason){
    return value.trim().length > 2;
  }

  render () {

    let value = this.props.filterValue

    let inputProps = {
      placeholder: '',
      value,
      onChange: this.handleOntoValue
    };

    return (
      <Autosuggest
        suggestions={this.state.options}
        onSuggestionsFetchRequested={this.onSuggestionsFetchRequested}
        onSuggestionsClearRequested={this.onSuggestionsClearRequested}
        getSuggestionValue={this.getSuggestionValue}
        renderSuggestion={this.renderSuggestion}
        inputProps={inputProps}
        renderInputComponent={this.renderInputComponent}
        shouldRenderSuggestions={this.shouldRenderSuggestions}        
      />
    )

  }
}

Autocomplete.propTypes = {
  handleFilterValue: PropTypes.func,
  entityUri: PropTypes.string,
  attributeId: PropTypes.number,
  filterValue: PropTypes.string,
  config: PropTypes.object,
}
