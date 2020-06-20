import React, { useState } from "react";

export const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function validateForm() {
    return email.length > 0 && password.length > 0;
  }

  function handleSubmit(event) {
    event.preventDefault();
  }

  return (
    <div>
        <h1>Login</h1>
        <form onSubmit={handleSubmit}>
            <label htmlFor="email">Email</label>
            <input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="Enter Email" name="email" required></input>

            <label htmlFor="psw">Password</label>
            <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="Enter Password" name="psw" required></input>

            <input disabled={!validateForm()} type="submit" value="Login"></input>
        </form>
    </div>
  );
}
