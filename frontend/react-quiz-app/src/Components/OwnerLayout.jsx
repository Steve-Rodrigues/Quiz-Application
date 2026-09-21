import { useAuth } from "./AuthContext";
import { Outlet, Navigate,Link } from "react-router-dom";
import { Loading } from './Loading.jsx';
export function OwnerLayout(){
    const {user, loading, logout} = useAuth();
    if(loading){
        return <Loading label="Loading" />;
    }
    if(!user){
        return <Navigate to='/login'/>
    }
        return(
            <>
            <div className='nav'>
                <div className='quizContain login'><div className='white-square'>Q</div> Quiz Builder</div>
                <div className='nav-user-space'>
                    <Link to='/quizzes/new' className="link-inline-nav">+ New Quiz</Link>
                    <div className="user-circle">{user.display_name[0]}</div>
                    <button type="button" className="logout-btn" onClick={logout}>Log out</button>
                </div>
            </div>
            <Outlet/>
            </>
        );
}