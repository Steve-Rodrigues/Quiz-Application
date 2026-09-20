import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchApi } from '../api.js';

export function QuizDashboard(){
    const { quizId } = useParams();
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchApi(`/api/quizzes/${quizId}/dashboard`)
            .then(setResults)
            .catch(e => setError(e.message))
            .finally(() => setLoading(false));
    }, [quizId]);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>{error}</p>;
    if (results.length === 0) return <p>No attempts yet.</p>;

    return (
        <>
        <h1>Results</h1>
        <table>
            <thead>
                <tr><th>Rank</th><th>Name</th><th>Score</th></tr>
            </thead>
            <tbody>
                {results.map((r, i) => (
                    <tr key={r.display_name}>
                        <td>{i + 1}</td>
                        <td>{r.display_name}</td>
                        <td>{r.score} / {r.total}</td>
                    </tr>
                ))}
            </tbody>
        </table>
        </>
    );
}