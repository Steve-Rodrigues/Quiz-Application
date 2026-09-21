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
        <div className='heroContainer'>
        <div className='leftHero'>
            <div className='quizContain'><div className='white-square'>Q</div> Quiz Builder</div>
            <h1>Build quizzes people actually want to take.</h1>
            <p>Create, share, and track results in minutes -- no setup required.</p>
            <ul>
                <li><input type="checkbox" className="signup"/>Build a quiz in minutes</li>
                <li><input type="checkbox" className="signup"/>Share with a single link</li>
                <li><input type="checkbox" className="signup"/>See live results as they come in</li>
            </ul>
        </div>
        <div className='rightHero'>
        <form onSubmit={handleSubmit}>
            <h2>Create your account</h2>
            <p className='text-muted'>Start building your first quiz</p>
            <div className='form-inputs'>
            <div className='field'>
                <p className='label'>Display Name</p>
                <input type="text" value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder='Joe Connor'/>
            </div>
            <div className='field'>
                <p className='label'>Email</p>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder='you@example.com'/>
            </div>
            <div className='field'>
                <p className='label'>Password</p>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}/>
            </div>
            <button type="submit">Create Account</button>
            </div>
        </form>
        <div className='login-bottom'>
        <p className='text-muted'>Already have an account? <Link to='/login' className='link-inline'>Log in</Link> </p>
        </div>
        </div>
        </div>
        </>
    );
}