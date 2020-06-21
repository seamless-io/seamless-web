import React, { useState } from "react";

import { logInUser } from '../../api';

class LoginForm extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            email: '',
            password: '',
            remember: false
        };

        this.onSubmit = this.onSubmit.bind(this);
        this.onEmailChange = this.onEmailChange.bind(this);
        this.onPasswordChange = this.onPasswordChange.bind(this);
        this.onRememberChange = this.onRememberChange.bind(this);
    }

    onEmailChange(event) {
        this.setState({email: event.target.value});
    }

    onPasswordChange(event) {
        this.setState({password: event.target.value});
    }

    onRememberChange(event) {
        this.setState({remember: event.target.value});
    }

    onSubmit(event) {
        logInUser(this.state.email, this.state.password, this.state.remember)
            .then((resp) => {
                console.log(resp);
            })
            .catch((err) => {
                console.log(err);
            });
        event.preventDefault();
    }

    render() {
      return (
        <div>
            <h1>Login</h1>
            <form onSubmit={this.onSubmit}>
                <label htmlFor="email">Email</label>
                <input value={this.state.email} onChange={this.onEmailChange.bind(this)} type="email" placeholder="Enter Email" name="email" required></input>

                <label htmlFor="password">Password</label>
                <input value={this.state.password} onChange={this.onPasswordChange.bind(this)} type="password" placeholder="Enter Password" name="password" required></input>

                <label htmlFor="remember">Remember me</label>
                <input name="remember" type="checkbox" checked={this.state.remember} onChange={this.onRememberChange.bind(this)} />

                <input type="submit" value="Login"></input>
            </form>
        </div>
      )
    };
}

export default LoginForm;
