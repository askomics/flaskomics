import React from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';

class App extends React.Component {

    get_message() {
    axios.get('/api/hello')
        .then( (response) => {
            console.log("response", response.data);
        })
        .catch( (error) => {
            console.log(error);
        });
    }

    render() {
        return (
            <div>
                <p>Welcome to AskOmics!</p>
                <button onClick={this.get_message}>Message</button>
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
