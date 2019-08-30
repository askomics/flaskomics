import React, { Component } from 'react'
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, ButtonGroup, Input } from 'reactstrap'
import UploadForm from './uploadform'
import UploadUrlForm from './uploadurlform'
import PropTypes from 'prop-types'

export default class UploadModal extends Component {
  constructor (props) {
    super(props)

    this.state = {
      modalComputer: false,
      modalUrl: false
    }
    this.toggleModalComputer = this.toggleModalComputer.bind(this)
    this.toggleModalUrl = this.toggleModalUrl.bind(this)
  }

  toggleModalComputer () {
    this.setState({
      modalComputer: !this.state.modalComputer
    })
  }

  toggleModalUrl () {
    this.setState({
      modalUrl: !this.state.modalUrl
    })
  }

  render () {
    return (

      <div>
        <ButtonGroup>
          <Button color="secondary" onClick={this.toggleModalComputer}><i className="fas fa-upload"></i> Computer</Button>
          <Button color="secondary" onClick={this.toggleModalUrl}><i className="fas fa-upload"></i> URL</Button>
          <Button color="secondary"><i className="fas fa-upload"></i> Galaxy</Button>
        </ButtonGroup>

        <Modal isOpen={this.state.modalComputer} toggle={this.toggleModalComputer}>
          <ModalHeader toggle={this.toggleModalComputer}>Upload files</ModalHeader>
          <ModalBody>
            <UploadForm setStateUpload={this.props.setStateUpload} />
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModalComputer}>Close</Button>
          </ModalFooter>
        </Modal>

        <Modal isOpen={this.state.modalUrl} toggle={this.toggleModalUrl}>
          <ModalHeader toggle={this.toggleModalUrl}>Upload files by URL</ModalHeader>
          <ModalBody>
            <UploadUrlForm setStateUpload={this.props.setStateUpload} />
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModalUrl}>Close</Button>
          </ModalFooter>
        </Modal>

      </div>
    )
  }
}

UploadModal.propTypes = {
  setStateUpload: PropTypes.func
}