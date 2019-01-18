import React from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

import Routes from './routes'

class App extends React.Component {

    render() {
        return (
            <Routes />
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
