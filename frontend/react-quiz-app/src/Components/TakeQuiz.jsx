import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchApi } from '../api.js';

export function TakeQuiz(){
    const { link } = useParams();

    const [displayName, setDisplayName] = useState('');
    const [started, setStarted] = useState(false);
    const [quiz, setQuiz] = useState(null);
    const [picks, setPicks] = useState({});
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    async function handleStart(e){
        e.preventDefault();
        setError('');
        setLoading(true);
        try{
            await fetchApi(`/api/quizzes/take/${link}/check-name?display_name=${encodeURIComponent(displayName)}`);
            const data = await fetchApi(`/api/quizzes/${link}/start-quiz`);
            setQuiz(data);
            setStarted(true);
        } catch(err){
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    function handlePick(questionId, answerId){
        setPicks(prev => ({...prev, [questionId]: answerId}));
    }

    async function handleSubmit(e){
        e.preventDefault();
        setError('');
        try{
            const picksArray = Object.entries(picks).map(([question_id, answer_id]) => ({
                question_id: Number(question_id),
                answer_id: answer_id
            }));
            const data = await fetchApi(`/api/quizzes/${link}/submit`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ display_name: displayName, picks: picksArray })
            });
            setResult(data);
        } catch(err){
            setError(err.message);
        }
    }

    if (result) {
        return (
            <>
                <h1>Results</h1>
                <p>{result.score} / {result.total} ({result.percentage_right}%)</p>
            </>
        );
    }

    if (!started) {
        return (
            <form onSubmit={handleStart}>
                {error && <p>{error}</p>}
                <label>Your Name</label>
                <input type="text" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
                <button type="submit" disabled={loading}>Start Quiz</button>
            </form>
        );
    }

    return (
        <form onSubmit={handleSubmit}>
            {error && <p>{error}</p>}
            <h1>{quiz.title}</h1>
            <p>{quiz.description}</p>
            {quiz.questions.map(q => (
                <div key={q.id}>
                    <p>{q.prompt}</p>
                    {q.answers.map(a => (
                        <label key={a.id}>
                            <input
                                type="radio"
                                name={`question-${q.id}`}
                                value={a.id}
                                checked={picks[q.id] === a.id}
                                onChange={() => handlePick(q.id, a.id)}
                            />
                            {a.text}
                        </label>
                    ))}
                </div>
            ))}
            <button type="submit">Submit Quiz</button>
        </form>
    );
}