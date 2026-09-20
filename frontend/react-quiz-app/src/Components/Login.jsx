//login component-- has form for info, on submit calls the handleSubmit function which just sets the state of the user to the user info
//entered in the form and depending on the result of the fetch we navigate to the quizzes route. keep states of uname and email being entered
import { useState } from 'react'
import { fetchApi } from '../api.js'
import { useAuth } from './AuthContext.jsx'
import { useNavigate } from 'react-router-dom';

export function Login(){
    const {login} = useAuth(); //all the context needed for login
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');//error state for bad login attempt
    const navigate = useNavigate();
    //call the login endpoint-- if we get user back, we set the user, else navigate to login again
    async function handleSubmit(e){
        e.preventDefault();
        try{
        const userData = await fetchApi('/api/auth/login',{
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        login(userData);
        navigate('/quizzes');
    }
        catch(err){
            setError(err.message);
        }
    }
    return(
        <>
        {error && <p>Login attempt failed</p>}
        <form onSubmit={handleSubmit}>
            <p>Username</p>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}/><br></br>
            <p>Password</p>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}/>
            <button type="submit">Log In</button>
        </form>
        </>
    );
}