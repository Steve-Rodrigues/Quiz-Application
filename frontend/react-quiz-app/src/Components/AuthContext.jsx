import { useState, useEffect, createContext, useContext } from 'react'
import { fetchApi } from '../api.js';
//going to create auth component to hold user state, if null we redirect to login. this component just returns the login, logout and user state
//we use each to change the state of user via the context that we wrap the components in and create here
const AuthContext = createContext();
export function AuthProvider({children}){
    const [user, setUser] = useState(null);//null to start (not logged in until we known from fetch result)
    const [loading, setLoading] = useState(true);//loading at first so we dont say no user right away
    useEffect(() => {
        fetchApi('/me')
        .then(userData => setUser(userData))
        .catch(() => setUser(null))
        .finally(() => setLoading(false));
    },[]);//runs once on mount, first time user opens the page(checks if previous sessions if not user is null to start)
    function login(data){
        setUser(data);//updates user state to hold the user info
    }
    function logout(){
        fetchApi('/logout',{method:'POST'}).finally(() => setUser(null));
    }
    return(
        <AuthContext.Provider value={{user, login, logout,loading}}>
            {children}
        </AuthContext.Provider>
    );
}
export function useAuth(){
    return useContext(AuthContext);
}//components import this so they can access the states