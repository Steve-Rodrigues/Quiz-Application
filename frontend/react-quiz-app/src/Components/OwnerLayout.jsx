import { useAuth } from "./AuthContext";
import { Outlet, Navigate,Link } from "react-router-dom";
export function OwnerLayout(){
    const {user, loading} = useAuth();
    if(loading){
        return(
            <>
            <p>Loading Content....</p>
            </>
        );
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
                </div>
            </div>
            <Outlet/>
            </>
        );
}