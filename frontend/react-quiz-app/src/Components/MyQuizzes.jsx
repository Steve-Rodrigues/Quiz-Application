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
            <h1>Quiz Dashboard</h1>
            <p>No Quizzes Created</p>
            </>
        )
    }
    return(
        <>
        <h1>Quiz Dashboard</h1>
        {
            allQuizzes.map(quiz => (
                <div key={quiz.id}>
                    <h2>{quiz.title}</h2>
                    {quiz.isPublished ? <Link to={`/quizzes/${quiz.id}/dashboard`}>Quiz Results</Link> : 
                    <Link to={`/quizzes/${quiz.id}/edit`}>Edit</Link>}
                </div>
            ))
        }
        </>
    )
}