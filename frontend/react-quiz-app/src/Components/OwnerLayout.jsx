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
            <nav>
                <p>Hello, {user.display_name}</p>
                <div>
                    <Link to='/quizzes/new'>Create Quiz</Link>
                </div>
            </nav>
            <Outlet/>
            </>
        );
}