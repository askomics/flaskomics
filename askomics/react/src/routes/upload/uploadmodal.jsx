import React, { Component } from "react"
import axios from 'axios'
import {  Button, Modal, ModalHeader, ModalBody, ModalFooter, ButtonGroup, FormText } from 'reactstrap'
import UploadForm from './uploadform'

export default class UploadModal extends Component {
  constructor(props) {
    super(props)

    this.state = {
      modal: false,
    }
    this.toggleModal = this.toggleModal.bind(this)
  }

  toggleModal() {
    this.setState({
      modal: !this.state.modal
    })
  }

  render() {
    return (

      <div>
        <ButtonGroup>
          <Button color="secondary" onClick={this.toggleModal}><i className="fas fa-upload"></i> Computer</Button>
          <Button color="secondary"><i className="fas fa-upload"></i> URL</Button>
          <Button color="secondary"><i className="fas fa-upload"></i> Galaxy</Button>
        </ButtonGroup>

        <Modal isOpen={this.state.modal} toggle={this.toggleModal}>
          <ModalHeader toggle={this.toggleModal}>Upload files</ModalHeader>
          <ModalBody>
            <UploadForm setStateUpload={this.props.setStateUpload} />
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModal}>Close</Button>
          </ModalFooter>
        </Modal>
      </div>
    )
  }
}
