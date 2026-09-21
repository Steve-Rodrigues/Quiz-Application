import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchApi } from '../api.js';
import { Loading } from './Loading.jsx';

export function QuizDashboard(){
    const { quizId } = useParams();
    const [results, setResults] = useState([]);
    const [quiz, setQuiz] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        //the dashboard endpoint only returns attempts, so the quiz itself is
        //fetched alongside it just for the title in the heading
        Promise.all([
            fetchApi(`/api/quizzes/${quizId}/dashboard`),
            fetchApi(`/api/quizzes/${quizId}`)
        ])
            .then(([attempts, quizData]) => {
                setResults(attempts);
                setQuiz(quizData);
            })
            .catch(e => setError(e.message))
            .finally(() => setLoading(false));
    }, [quizId]);

    if(loading) return <Loading label="Loading results" />;
    if(error) return <p className="form-error">{error}</p>;

    const heading = quiz ? quiz.title : 'Results';

    if(results.length === 0){
        return(
            <div className="dash-container">
                <div className="dash-head">
                    <h1>{heading}</h1>
                    <p className="text-muted">No attempts yet. Share the link to get scores in here.</p>
                </div>
                <Link to="/quizzes" className="link-inline">Back to My Quizzes</Link>
            </div>
        );
    }

    //every row carries the same total, so it can be read off the first one
    const total = results[0].total;
    const avgScore = results.reduce((sum, r) => sum + r.score, 0) / results.length;
    const avgPercent = total ? Math.round((avgScore / total) * 100) : 0;

    //the list arrives sorted by score descending, so the leader is simply the first row
    const top = results[0];
    const tiedAtTop = results.filter(r => r.score === top.score).length - 1;

    //a tie takes the rank of the first row holding that score, so two people on the
    //same score both read as 2nd instead of 2nd and 3rd
    const ranks = results.map((r, i) => {
        let rank = i;
        while(rank > 0 && results[rank - 1].score === r.score) rank--;
        return rank + 1;
    });

    return(
        <div className="dash-container">
            <div className="dash-head">
                <h1>{heading}</h1>
                <p className="text-muted">Results for everyone who has taken this quiz.</p>
            </div>

            <div className="stat-cards">
                <div className="stat-card">
                    <p className="stat-label">Attempts</p>
                    <p className="stat-value">{results.length}</p>
                    <p className="text-muted">{results.length === 1 ? 'person has taken it' : 'people have taken it'}</p>
                </div>
                <div className="stat-card">
                    <p className="stat-label">Average Score</p>
                    <p className="stat-value">{avgScore.toFixed(1)} / {total}</p>
                    <p className="text-muted">{avgPercent}% across all attempts</p>
                </div>
                <div className="stat-card">
                    <p className="stat-label">Top Score</p>
                    <p className="stat-value">{top.score} / {total}</p>
                    <p className="text-muted">
                        {top.display_name}{tiedAtTop > 0 && ` +${tiedAtTop} tied`}
                    </p>
                </div>
            </div>

            <h2 className="createHeader">Leaderboard</h2>
            <table className="leaderboard">
                <thead>
                    <tr><th>Rank</th><th>Name</th><th>Score</th><th>Percent</th></tr>
                </thead>
                <tbody>
                    {results.map((r, i) => (
                        //display names are not guaranteed unique, so the row index is the key
                        <tr key={i} className={ranks[i] === 1 ? 'leader-row' : undefined}>
                            <td>{ranks[i]}</td>
                            <td>{r.display_name}</td>
                            <td>{r.score} / {r.total}</td>
                            <td>{r.total ? Math.round((r.score / r.total) * 100) : 0}%</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <Link to="/quizzes" className="link-inline">Back to My Quizzes</Link>
        </div>
    );
}
