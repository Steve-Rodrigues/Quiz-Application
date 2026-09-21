import { useState } from "react";
import { useAuth } from "./AuthContext";
import { Outlet, Navigate } from "react-router-dom";
import { Loading } from './Loading.jsx';

export function EditLayout(){
    const {user, loading, logout} = useAuth();
    //the buttons sit up here but the quiz form owns the state they act on, so the
    //child route hands its handlers up through the outlet context
    const [actions, setActions] = useState(null);

    if(loading){
        return(
            <>
            <Loading label="Loading" />
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
                    <button type="button" className="nav-btn" onClick={() => actions.onSave()}
                        disabled={!actions || actions.busy}>Save Changes</button>
                    <button type="button" className="nav-btn publish-btn" onClick={() => actions.onPublish()}
                        disabled={!actions || actions.busy}>
                        {actions && actions.busy ? 'Publishing...' : 'Publish Quiz'}
                    </button>
                    <div className="user-circle">{user.display_name[0]}</div>
                    <button type="button" className="logout-btn" onClick={logout}>Log out</button>
                </div>
            </div>
            <Outlet context={{ setActions }}/>
            </>
        );
}
