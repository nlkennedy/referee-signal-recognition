import React from 'react';
import {Link} from 'react-router';

class About extends React.Component {
    render() {
        return (
            <div>
                <div class="container" style={{ marginTop: '5%' }}>
                    <h1> About </h1>
                    <p>
                        This app is an auto referee hand signal detection and score keep app for the Tufts University Squash team.
                    </p>
                    <p>
                        This app was built by Ben Bodine, Harsh Prajapati, Nicole Kennedy, and Radhika Joshi. 
                    </p>
                    <p>
                        About us About us About us About us About us About us About us About us 
                        About us About us About us About us About us About us About us About us 
                        About us About us About us About us About us About us About us About us 
                        About us About us About us About us About us About us About us About us 
                        About us About us About us About us About us About us About us About us 
                        About us About us About us About us About us About us About us About us 
                    </p>
                </div>

                <footer class="footer">
                    <div class="container h-100 d-flex justify-content-center align-items-center">
                        <a class="nav-link" href="/">Back to Home</a>
                    </div>
                </footer>
            </div>
        )
    }
}

export default About;