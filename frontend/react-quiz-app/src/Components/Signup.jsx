import { useState } from 'react'
import { fetchApi } from '../api.js'
import { Link,useNavigate } from 'react-router-dom';
export function Signup(){
    const [email, setEmail] = useState('');
    const [displayName, setDisplayName] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const nav = useNavigate();
    async function handleSubmit(e){
        e.preventDefault();
        try{
        const user = await fetchApi('/api/auth/signup',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({email, display_name: displayName, password})
        });
        nav('/login');
    }catch(err){
        setError(err.message);
    }
    }
    return(
        <>
        {error && <p>{error}</p>}
        <h1>Register</h1>
        <form onSubmit={handleSubmit}>
            <p>Display Name</p>
            <input type="text" value={displayName} onChange={(e) => setDisplayName(e.target.value)}/>
            <p>Email</p>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}/>
            <p>Password</p>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}/>
            <button type="submit">Create Account</button>
        </form>
        <h3>Or if already have account go to login</h3>
        <Link to='/login'>Login</Link>
        </>
    );
}