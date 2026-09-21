//catch-all for the * route-- reached by a mistyped url or a dead share link.
//sits outside OwnerLayout, so it has to read for a logged out taker as well as the owner
import { Link } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';

export function NotFound(){
    const { user, loading } = useAuth();

    return(
        <div className="take-container">
            <div className="notfound-card">
                <div className="quizContain login"><div className="white-square">Q</div> Quiz Builder</div>
                <p className="notfound-code">404</p>
                <h2 className="createHeader">Page not found</h2>
                <p className="text-muted">
                    That link does not lead anywhere. If it was a shared quiz link, check it
                    was copied in full, or ask whoever sent it for a new one.
                </p>
                {/* the session is still resolving on first paint, so hold the link back
                    rather than flash one that points the wrong way */}
                {!loading && (
                    user
                        ? <Link to="/quizzes" className="card-link">Back to My Quizzes</Link>
                        : <Link to="/login" className="card-link">Go to Log In</Link>
                )}
            </div>
        </div>
    );
}
