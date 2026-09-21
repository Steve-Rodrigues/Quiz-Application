//the public side of the app-- reached by the share link, no login involved.
//three screens off the one route: name gate -> questions -> result
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
    const [submitting, setSubmitting] = useState(false);

    async function handleStart(e){
        e.preventDefault();
        //the backend hands out any name that is not already taken, including a blank one
        if(!displayName.trim()){
            setError('Enter a name so your score can be identified.');
            return;
        }
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
        if(submitting) return;

        //anything left blank is simply absent from picks and scores zero, so say so first
        const unanswered = quiz.questions.filter(q => picks[q.id] === undefined).length;
        if(unanswered > 0){
            const word = unanswered === 1 ? 'question' : 'questions';
            if(!window.confirm(`${unanswered} ${word} left unanswered. They will be marked wrong. Submit anyway?`)) return;
        }

        setError('');
        setSubmitting(true);
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
            //only let them try again on a failure-- a success must not be resubmitted,
            //the name check happens at start so a second submit would post a duplicate
            setSubmitting(false);
        }
    }

    if(result){
        return(
            <div className="take-container">
                <div className="take-card take-result">
                    <div className="quizContain login"><div className="white-square">Q</div> Quiz Builder</div>
                    <h2 className="createHeader">Quiz Complete</h2>
                    <p className="text-muted">Nice work, {displayName}.</p>
                    <p className="result-score">{result.score} / {result.total}</p>
                    <p className="result-percent">{result.percentage_right}%</p>
                    <p className="text-muted">Your score has been added to the leaderboard.</p>
                </div>
            </div>
        );
    }

    if(!started){
        return(
            <div className="take-container">
                <form className="take-card" onSubmit={handleStart}>
                    <div className="quizContain login"><div className="white-square">Q</div> Quiz Builder</div>
                    <h2 className="createHeader">You have been invited to a quiz</h2>
                    <p className="text-muted">Pick a name to show on the leaderboard.</p>
                    <div className="form-inputs">
                        <div className="field">
                            <p className="label">Your Name</p>
                            <input type="text" value={displayName} placeholder="e.g. Sam"
                                onChange={(e) => setDisplayName(e.target.value)} />
                        </div>
                        <button type="submit" disabled={loading}>
                            {loading ? 'Starting...' : 'Start Quiz'}
                        </button>
                    </div>
                    {error && <p className="form-error">{error}</p>}
                </form>
            </div>
        );
    }

    const answered = quiz.questions.filter(q => picks[q.id] !== undefined).length;

    return(
        <div className="take-container">
            <form className="take-form" onSubmit={handleSubmit}>
                <div className="take-head">
                    <h1>{quiz.title}</h1>
                    <p className="text-muted">{quiz.description}</p>
                    <p className="take-progress">{answered} of {quiz.questions.length} answered</p>
                </div>
                <div className="line-seperate"></div>

                {quiz.questions.map((q, index) => (
                    <div key={q.id} className="question">
                        <label className="questionNum">Question {index + 1}</label>
                        <p className="take-prompt">{q.prompt}</p>
                        <div className="questionsWrapped">
                        {q.answers.map(a => (
                            //the whole row is the label so clicking anywhere on it picks the answer
                            <label key={a.id}
                                className={picks[q.id] === a.id ? 'take-answer picked' : 'take-answer'}>
                                <input type="radio" name={`question-${q.id}`} value={a.id}
                                    checked={picks[q.id] === a.id}
                                    onChange={() => handlePick(q.id, a.id)} />
                                <span>{a.text}</span>
                            </label>
                        ))}
                        </div>
                    </div>
                ))}

                {error && <p className="form-error">{error}</p>}
                <button type="submit" disabled={submitting}>
                    {submitting ? 'Submitting...' : 'Submit Quiz'}
                </button>
            </form>
        </div>
    );
}
