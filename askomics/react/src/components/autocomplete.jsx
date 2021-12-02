import React, { Component} from 'react'
import axios from 'axios'
import PropTypes from 'prop-types'
import TextInput from 'react-autocomplete-input';
import 'react-autocomplete-input/dist/bundle.css';

export default class Autocomplete extends Component {
  constructor (props) {
    super(props)
    this.state = {
        ontologyShort: this.getAutoComplete(),
        options: []
    }

    this.handleFilterValue = this.props.handleFilterValue.bind(this)
    this.autocompleteOntology = this.autocompleteOntology.bind(this)
    this.cancelRequest
  }

  getAutoComplete () {
      return this.props.config.ontologies.map(onto => {
        if (onto.uri == this.props.entityUri) {
          return onto.short_name
        } else {
          return null
        }
      })
  }

  autocompleteOntology (value) {
    let userInput = value
    let requestUrl = '/api/ontology/' + this.state.ontologyShort + "/autocomplete"
    axios.get(requestUrl, {baseURL: this.props.config.proxyPath, params:{q: userInput}, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log(requestUrl, response.data)
        // set state of resultsPreview
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

  renderAutocomplete () {
    
    let input = (<div>
      <TextInput trigger="" matchAny={true} spacer="" minChars={3} Component="input" options={this.state.options} onChange={(e) => this.handleFilterValue({target: {value: e, id: this.props.attributeId}})} id={this.props.attributeId} value={this.props.filterValue} onRequestOptions={this.autocompleteOntology}/>
    </div>)

    return input
  }

  render () {
    return this.renderAutocomplete()
  }
}

Autocomplete.propTypes = {
  handleFilterValue: PropTypes.func,
  entityUri: PropTypes.string,
  attributeId: PropTypes.number,
  filterValue: PropTypes.string,
  config: PropTypes.object,
}
