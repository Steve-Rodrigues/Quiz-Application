import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchApi } from '../api.js';

export function CreateQuizzes(){
    const navigate = useNavigate();
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [questions, setQuestions] = useState([]);
    const [error, setError] = useState('');

    function handleTitleChange(e){
        setTitle(e.target.value);
    }
    function toggleCorrect(qid, aid) {
    setQuestions(prev => prev.map(q =>
        q.id === qid
            ? {...q, answers: q.answers.map(a => ({...a, isCorrect: a.id === aid}))}
            : q
    ));
}
    function handleDescChange(e){
        setDescription(e.target.value);
    }
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
    async function handleSubmit(e){
        e.preventDefault();
        try{
            const cleanQuestions = questions.map(q => ({
                prompt: q.prompt,
                answers: q.answers.map(a => ({ text: a.text, isCorrect: a.isCorrect }))
            }));
            const quiz = { title, description, questions: cleanQuestions };
            await fetchApi('/api/quizzes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(quiz)
            });
            navigate('/quizzes');
        }
        catch(err){
            setError(err.message);
        }
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
        ))
    }
    function addAnswer(qid){
        setQuestions(q => q.map(obj => (
            obj.id == qid ? {...obj, answers:[...obj.answers,{id: crypto.randomUUID(),text:'',isCorrect:false} ]}: obj
        )));
    }
    return(
        <>
        <div className="create-Container">
        <form onSubmit={handleSubmit}>
            {error && <p>{error}</p>}
            <label>Quiz Title</label>
            <input type="text" value={title} onChange={handleTitleChange} />

            <label>Description</label>
            <textarea value={description} onChange={handleDescChange} />
            <label>Questions</label>
            <div className="questions-container">
            {questions.map(q => (
                <div key={q.id}>
                    <input type="text" placeholder="Question Prompt" value={q.prompt}
                        onChange={(e) => handlePrompt(q.id, e)} />
                    {q.answers.map(a => (
                        <div key={a.id}>
                            <input type="text" value={a.text} placeholder="Answer Text"
                                onChange={(e) => updateAnswerText(q.id, a.id, e)} />
                            <input type="checkbox" onChange={() => toggleCorrect(q.id, a.id)}/>
                        </div>
                    ))}
                    <button type="button" onClick={() => addAnswer(q.id)}>Add Answer</button>
                </div>
            ))}
            </div>
            <button type="button" onClick={addQuestion}>Add Question</button>
            <button type="submit">Create Quiz</button>
        </form>
        </div>
        </>
    )
}