import React, { Component } from 'react'
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, ButtonGroup, Input } from 'reactstrap'
import UploadForm from './uploadform'
import UploadUrlForm from './uploadurlform'
import UploadGalaxyForm from './uploadgalaxyform'
import PropTypes from 'prop-types'

export default class UploadModal extends Component {
  constructor (props) {
    super(props)

    this.state = {
      modalComputer: false,
      modalUrl: false,
      modalGalaxy: false
    }
    this.toggleModalComputer = this.toggleModalComputer.bind(this)
    this.toggleModalUrl = this.toggleModalUrl.bind(this)
    this.toggleModalGalaxy = this.toggleModalGalaxy.bind(this)
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

  toggleModalGalaxy () {
    this.setState({
      modalGalaxy: !this.state.modalGalaxy
    })
  }

  render () {

    let galaxyForm
    let galaxyButton
    if (this.props.config.user.galaxy) {
      galaxyForm = (
        <Modal size="lg" isOpen={this.state.modalGalaxy} toggle={this.toggleModalGalaxy}>
          <ModalHeader toggle={this.toggleModalGalaxy}>Upload Galaxy datasets</ModalHeader>
          <ModalBody>
            <UploadGalaxyForm config={this.props.config} getQueries={false} setStateUpload={this.props.setStateUpload} />
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModalGalaxy}>Close</Button>
          </ModalFooter>
        </Modal>
      )
      galaxyButton = <Button color="secondary" onClick={this.toggleModalGalaxy}><i className="fas fa-upload"></i> Galaxy</Button>
    }

    return (
      <div>
        <ButtonGroup>
          <Button color="secondary" onClick={this.toggleModalComputer}><i className="fas fa-upload"></i> Computer</Button>
          <Button color="secondary" onClick={this.toggleModalUrl}><i className="fas fa-upload"></i> URL</Button>
          {galaxyButton}
        </ButtonGroup>

        <Modal isOpen={this.state.modalComputer} toggle={this.toggleModalComputer}>
          <ModalHeader toggle={this.toggleModalComputer}>Upload files</ModalHeader>
          <ModalBody>
            <UploadForm config={this.props.config} setStateUpload={this.props.setStateUpload} />
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModalComputer}>Close</Button>
          </ModalFooter>
        </Modal>

        <Modal isOpen={this.state.modalUrl} toggle={this.toggleModalUrl}>
          <ModalHeader toggle={this.toggleModalUrl}>Upload files by URL</ModalHeader>
          <ModalBody>
            <UploadUrlForm config={this.props.config} setStateUpload={this.props.setStateUpload} />
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={this.toggleModalUrl}>Close</Button>
          </ModalFooter>
        </Modal>
        {galaxyForm}
      </div>
    )
  }
}

UploadModal.propTypes = {
  setStateUpload: PropTypes.func,
  config: PropTypes.object
}