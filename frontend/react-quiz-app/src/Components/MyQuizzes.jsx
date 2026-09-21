import { fetchApi } from "../api.js";
import { useState,useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Loading } from './Loading.jsx';

function shareUrl(quiz){
    return `${window.location.origin}/take/${quiz.share_link}`;
}

export function MyQuizzes(){
    const [error, setError] = useState('');
    const [allQuizzes, setAllQuizzes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [copiedId, setCopiedId] = useState(null);
    const [copyFailedId, setCopyFailedId] = useState(null);
    const [deletingId, setDeletingId] = useState(null);
    const [deleteError, setDeleteError] = useState(null);

    useEffect(() => {
        fetchApi('/api/quizzes')
        .then(data => setAllQuizzes(data))
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false))
    },[]);

    async function copyLink(quiz){
        try{
            await navigator.clipboard.writeText(shareUrl(quiz));
            setCopiedId(quiz.id);
            setCopyFailedId(null);
        }
        catch{
            //clipboard is blocked outside https, so fall back to an input they can copy by hand
            setCopiedId(null);
            setCopyFailedId(quiz.id);
        }
    }

    //only drafts can be deleted, the backend rejects it once a quiz is published
    async function deleteQuiz(quiz){
        if(!window.confirm(`Delete "${quiz.title}"? This cannot be undone.`)) return;
        setDeletingId(quiz.id);
        setDeleteError(null);
        try{
            await fetchApi(`/api/quizzes/${quiz.id}`, { method: 'DELETE' });
            setAllQuizzes(quizzes => quizzes.filter(q => q.id !== quiz.id));
        }
        catch(e){
            //keep the list on screen and put the message on the card that failed
            setDeleteError({ id: quiz.id, message: e.message });
        }
        finally{
            setDeletingId(null);
        }
    }

    if(loading){
        return <Loading label="Loading your quizzes" />
    }
    if(error){
        return(
            <p>{error}</p>
        )
    }
    if(allQuizzes.length === 0){
        return(
            <>
            <h1>My quizzes</h1>
            <p>No Quizzes Created</p>
            </>
        )
    }
    return(
        <>
        <div className="quizzes-container">
        <h1>My Quizzes</h1>
        <div className="quiz-card-cont">
        {
            allQuizzes.map(quiz => (
                <div className="quiz-card" key={quiz.id}>
                    {quiz.isPublished ? <div className="publish-circle">Published</div> : <div className="draft-circle">Draft</div>}
                    <div className="quiz-card-body">
                        <h2>{quiz.title}</h2>
                        <p className="text-muted">{quiz.description}</p>
                    </div>
                    <div className="quiz-card-footer">
                        <Link className="card-link"
                            to={quiz.isPublished ? `/quizzes/${quiz.id}/dashboard` : `/quizzes/${quiz.id}/edit`}>
                            {quiz.isPublished ? 'Quiz Results' : 'Edit'}
                        </Link>
                        {quiz.isPublished && quiz.share_link &&
                            <button type="button" className="copy-btn" onClick={() => copyLink(quiz)}>
                                {copiedId === quiz.id ? 'Copied' : 'Copy link'}
                            </button>
                        }
                        {!quiz.isPublished &&
                            <button type="button" className="delete-btn"
                                disabled={deletingId === quiz.id}
                                onClick={() => deleteQuiz(quiz)}>
                                {deletingId === quiz.id ? 'Deleting...' : 'Delete'}
                            </button>
                        }
                    </div>
                    {deleteError?.id === quiz.id && <p className="form-error">{deleteError.message}</p>}
                    {copyFailedId === quiz.id &&
                        <input className="share-input" type="text" readOnly
                            value={shareUrl(quiz)}
                            onFocus={(e) => e.target.select()} />
                    }
                </div>
            ))
        }
        </div>
        </div>
        </>
    )
}
