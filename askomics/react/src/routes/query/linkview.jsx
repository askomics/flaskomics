import React, { Component } from 'react'
import axios from 'axios'
import { Input, FormGroup, CustomInput, Col, Row, Button } from 'reactstrap'
import { Redirect } from 'react-router-dom'
import ErrorDiv from '../error/error'
import WaitingDiv from '../../components/waiting'
import update from 'react-addons-update'
import Visualization from './visualization'
import PropTypes from 'prop-types'

export default class LinkView extends Component {
  constructor (props) {
    super(props)
    this.handleChangePosition = this.props.handleChangePosition.bind(this)
    this.handleClickReverse = this.props.handleClickReverse.bind(this)
    this.handleChangeSameRef = this.props.handleChangeSameRef.bind(this)
    this.handleChangeSameStrand = this.props.handleChangeSameStrand.bind(this)
    this.handleChangeStrict = this.props.handleChangeStrict.bind(this)
    this.nodesHaveRefs = this.props.nodesHaveRefs.bind(this)
    this.nodesHaveStrands = this.props.nodesHaveStrands.bind(this)
    this.toggleAddFaldoFilter = this.props.toggleAddFaldoFilter.bind(this)
    this.toggleRemoveFaldoFilter = this.props.toggleRemoveFaldoFilter.bind(this)
    this.handleFaldoModifierSign = this.props.handleFaldoModifierSign.bind(this)
    this.handleFaldoFilterSign = this.props.handleFaldoFilterSign.bind(this)
    this.handleFaldoFilterStart = this.props.handleFaldoFilterStart.bind(this)
    this.handleFaldoFilterEnd = this.props.handleFaldoFilterEnd.bind(this)
    this.handleFaldoValue = this.props.handleFaldoValue.bind(this)
  }


  subNums (id) {
    let newStr = ""
    let oldStr = id.toString()
    let arrayString = [...oldStr]
    arrayString.forEach(char => {
      let code = char.charCodeAt()
      newStr += String.fromCharCode(code + 8272)
    })
    return newStr
  }

  render () {
    const sign_display = {
      '=': '=',
      '<': '<',
      '<=': '≤',
      '>': '>',
      '>=': '≥',
      '!=': '≠'
    }

    const modifier_display = {
      '+': '+',
      '-': '-',
    }

    const position_display = {
      'start': 'start',
      'end': 'end'
    }

    const numberOfFilters = this.props.link.faldoFilters.length - 1

    let modifier = <CustomInput onChange={this.handleChangeStrict} checked={this.props.link.strict ? true : false} value={this.props.link.strict ? true : false} type="checkbox" id={"strict-" + this.props.link.id} label="Strict" />
    if (this.props.link.uri == 'distance_from'){
      modifier = (
        <table style={{ width: '100%' }}>
        {this.props.link.faldoFilters.map((filter, index) => {
          return (
            <tr key={index}>
              <td>
                <CustomInput key={index} data-index={index} type="select" id={this.props.link.id} onChange={this.handleFaldoFilterStart}>
                  {Object.keys(position_display).map(sign => {
                    return <option key={sign} selected={filter.filterStart == sign ? true : false} value={sign}>{position_display[sign] + " " + this.props.link.source.label + this.subNums(this.props.link.source.humanId)}</option>
                  })}
                </CustomInput>
              </td>
              <td key={index}>
                <CustomInput key={index} data-index={index} type="select" id={this.props.link.id} onChange={this.handleFaldoFilterSign}>
                  {Object.keys(sign_display).map(sign => {
                    return <option key={sign} selected={filter.filterSign == sign ? true : false} value={sign}>{sign_display[sign]}</option>
                  })}
                </CustomInput>
              </td>
              <td>
                <CustomInput key={index} data-index={index} type="select" id={this.props.link.id} onChange={this.handleFaldoFilterEnd}>
                  {Object.keys(position_display).map(sign => {
                    return <option key={sign} selected={filter.filterEnd == sign ? true : false} value={sign}>{position_display[sign] + " " + this.props.link.target.label + this.subNums(this.props.link.target.humanId)}</option>
                  })}
                </CustomInput>
              </td>
              <td>
              <CustomInput key={index} data-index={index} type="select" id={this.props.link.id} onChange={this.handleFaldoModifierSign}>
                {Object.keys(modifier_display).map(sign => {
                  return <option key={sign} selected={filter.filterModifier == sign ? true : false} value={sign}>{modifier_display[sign]}</option>
                })}
              </CustomInput>
              </td>
              <td>
                <div className="input-with-icon">
                <Input size={4} className="input-with-icon" data-index={index} type="text" id={this.props.link.id} value={filter.filterValue} onChange={this.handleFaldoValue}/>
                {index == 0 && numberOfFilters == 0 ? <button className="input-with-icon"><i className="attr-icon fas fa-plus inactive" id={this.props.link.id} onClick={this.toggleAddFaldoFilter}></i></button> : <></>}
                {index == numberOfFilters && index > 0 ? <button className="input-with-icon"><i className="attr-icon fas fa-minus inactive" id={this.props.link.id} onClick={this.toggleRemoveFaldoFilter}></i></button> : <></>}
                </div>
              </td>
            </tr>
          )
        })}
        </table>
      )
    }

    return (
      <div className="container">
        <h5>Relation</h5>
        <hr />
        <table>
          <tr>
            <td>{this.props.link.source.label}</td>
            <td>
             <CustomInput type="select" id={this.props.link.id} name="position" onChange={this.handleChangePosition}>
                <option selected={this.props.link.uri == 'included_in' ? true : false} value="included_in">included in</option>
                <option selected={this.props.link.uri == 'overlap_with' ? true : false} value="overlap_with">overlap with</option>
                <option selected={this.props.link.uri == 'distance_from' ? true : false} value="distance_from">distant from</option>
              </CustomInput>
            </td>
            <td>{this.props.link.target.label}</td>
            <td>{"  "}</td>
            <td><Button id={this.props.link.id} color="secondary" size="sm" onClick={this.handleClickReverse}><i className="fas fa-exchange-alt"></i> Reverse</Button></td>
          </tr>
        </table>
        <br />
        {modifier}
        <br />
        {(this.nodesHaveRefs(this.props.link) || this.nodesHaveStrands(this.props.link)) && (
        <>
        <h5>On the same</h5>
        <hr />
        <CustomInput disabled={!this.nodesHaveRefs(this.props.link)} onChange={this.handleChangeSameRef} checked={this.props.link.sameRef ? true : false} value={this.props.link.sameRef ? true : false} type="checkbox" id={"sameref-" + this.props.link.id} label="Same reference" />
        <CustomInput disabled={!this.nodesHaveStrands(this.props.link)} onChange={this.handleChangeSameStrand} checked={this.props.link.sameStrand ? true : false} value={this.props.link.sameStrand ? true : false} type="checkbox" id={"samestrand-" + this.props.link.id} label="Same strand" />
        </>
        )}
      </div>
    )
  }
}

LinkView.propTypes = {
  link: PropTypes.object,
  handleChangePosition: PropTypes.func,
  handleClickReverse: PropTypes.func,
  handleChangeSameRef: PropTypes.func,
  handleChangeSameStrand: PropTypes.func,
  handleChangeStrict: PropTypes.func,
  nodesHaveRefs: PropTypes.func,
  nodesHaveStrands: PropTypes.func,
  toggleAddFaldoFilter: PropTypes.func,
  toggleRemoveFaldoFilter: PropTypes.func,
  handleFaldoModifierSign: PropTypes.func,
  handleFaldoFilterSign: PropTypes.func,
  handleFaldoFilterStart: PropTypes.func,
  handleFaldoFilterEnd: PropTypes.func,
  handleFaldoValue: PropTypes.func,
}
