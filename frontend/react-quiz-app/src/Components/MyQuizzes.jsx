import { fetchApi } from "../api.js";
import { useState,useEffect } from 'react';
import { Link } from 'react-router-dom';

export function MyQuizzes(){
    const [error, setError] = useState('');
    const [allQuizzes, setAllQuizzes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchApi('/api/quizzes')
        .then(data => setAllQuizzes(data))
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false))
    },[]);
    if(loading){
        return(
            <p>Loading...</p>
        )
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
                    {quiz.isPublished ? <div className="published-cirlce">Published</div> : <div className="draft-circle">Draft</div>}
                    <h2>{quiz.title}</h2>
                    <p className="text-muted">{quiz.description}</p>
                    {quiz.isPublished ? <Link to={`/quizzes/${quiz.id}/dashboard`}>Quiz Results</Link> : 
                    <Link to={`/quizzes/${quiz.id}/edit`} className="link-inline">Edit</Link>}
                </div>
            ))
        }
        </div>
        </div>
        </>
    )
}