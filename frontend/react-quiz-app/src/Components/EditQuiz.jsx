import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchApi } from '../api.js';

export function EditQuiz(){
    const { quizId } = useParams();
    const navigate = useNavigate();

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchApi(`/api/quizzes/${quizId}`)
            .then(data => {
                setTitle(data.title);
                setDescription(data.description);
                setQuestions(data.questions);
            })
            .catch(e => setError(e.message))
            .finally(() => setLoading(false));
    }, [quizId]);

    function handleTitleChange(e){ setTitle(e.target.value); }
    function handleDescChange(e){ setDescription(e.target.value); }

    function handlePrompt(id, e){
        setQuestions(q => q.map(obj => (
            id == obj.id ? {...obj, prompt: e.target.value} : obj
        )));
    }
    function updateAnswerText(qid, aid, e) {
        setQuestions(prev => prev.map(q =>
            q.id === qid
                ? {...q, answers: q.answers.map(a => a.id === aid ? {...a, text: e.target.value} : a)}
                : q
        ));
    }
    function toggleCorrect(qid, aid) {
        setQuestions(prev => prev.map(q =>
            q.id === qid
                ? {...q, answers: q.answers.map(a => ({...a, isCorrect: a.id === aid}))}
                : q
        ));
    }
    function addQuestion(){
        setQuestions(q => (
            [...q, {
                id: crypto.randomUUID(),
                prompt: '',
                answers: [
                    { id: crypto.randomUUID(), text: '', isCorrect: false },
                    { id: crypto.randomUUID(), text: '', isCorrect: false }
                ]
            }]
        ));
    }
    function addAnswer(qid){
        setQuestions(q => q.map(obj => (
            obj.id == qid ? {...obj, answers:[...obj.answers,{id: crypto.randomUUID(),text:'',isCorrect:false}]}: obj
        )));
    }

    async function handleSubmit(e){
        e.preventDefault();
        try{
            const cleanQuestions = questions.map(q => ({
                prompt: q.prompt,
                answers: q.answers.map(a => ({ text: a.text, isCorrect: a.isCorrect }))
            }));
            const quiz = { title, description, questions: cleanQuestions };
            await fetchApi(`/api/quizzes/${quizId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(quiz)
            });
            navigate('/quizzes');
        }
        catch(err){
            setError(err.message);
        }
    }

    if (loading) return <p>Loading...</p>;

    return(
        <>
        <form onSubmit={handleSubmit}>
            {error && <p>{error}</p>}
            <label>Title</label>
            <input type="text" value={title} onChange={handleTitleChange} />

            <label>Description</label>
            <textarea value={description} onChange={handleDescChange} />

            {questions.map(q => (
                <div key={q.id}>
                    <input type="text" placeholder="Question Prompt" value={q.prompt}
                        onChange={(e) => handlePrompt(q.id, e)} />
                    {q.answers.map(a => (
                        <div key={a.id}>
                            <input type="text" value={a.text} placeholder="Answer Text"
                                onChange={(e) => updateAnswerText(q.id, a.id, e)} />
                            <input type="checkbox" checked={a.isCorrect}
                                onChange={() => toggleCorrect(q.id, a.id)} />
                        </div>
                    ))}
                    <button type="button" onClick={() => addAnswer(q.id)}>Add Answer</button>
                </div>
            ))}
            <button type="button" onClick={addQuestion}>Add Question</button>
            <button type="submit">Save Changes</button>
        </form>
        </>
    )
}