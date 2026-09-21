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
    //questions and answers only live in local state until save, so removing one here is
    //enough-- PATCH clears and rebuilds the whole list from what gets sent
    function removeQuestion(qid){
        const target = questions.find(q => q.id === qid);
        //only worth a confirm once something has actually been typed into it
        const hasContent = target && (target.prompt.trim() || target.answers.some(a => a.text.trim()));
        if(hasContent && !window.confirm('Remove this question and its answers?')) return;
        setQuestions(q => q.filter(obj => obj.id !== qid));
    }
    function removeAnswer(qid, aid){
        setQuestions(q => q.map(obj => (
            obj.id === qid ? {...obj, answers: obj.answers.filter(a => a.id !== aid)} : obj
        )));
    }
    return(
        <>
        <div className="create-Container">
        <form onSubmit={handleSubmit}>
            {error && <p>{error}</p>}
            <label>Quiz Title</label>
            <input className="title-input" type="text" value={title} onChange={handleTitleChange} />

            <label>Description</label>
            <textarea value={description} onChange={handleDescChange} />
            <div className='line-seperate'></div>
            <h2 className='createHeader'>Questions</h2>
            <div className="questions-container">
            {questions.map((q, index) => (
                <div key={q.id} className="question">
                    <div className="question-head">
                        <label className='questionNum'>Question {index + 1}</label>
                        <button type="button" className="remove-question"
                            onClick={() => removeQuestion(q.id)}>Remove</button>
                    </div>
                    <input type="text" placeholder="Question Prompt" value={q.prompt}
                        onChange={(e) => handlePrompt(q.id, e)} />
                    <div className="questionsWrapped">
                    {q.answers.map(a => (
                        <div key={a.id} className="answerInput">
                            <input type="text" value={a.text} placeholder="Answer Text"
                                onChange={(e) => updateAnswerText(q.id, a.id, e)} />
                            <input type="checkbox" className="quizCheck" checked={a.isCorrect}
                                onChange={() => toggleCorrect(q.id, a.id)}/>
                            <button type="button" className="remove-answer"
                                aria-label="Remove answer"
                                onClick={() => removeAnswer(q.id, a.id)}>&times;</button>
                        </div>
                    ))}</div>
                    <button type="button" onClick={() => addAnswer(q.id)} className="answer-btn">+ Add Answer</button>
                </div>
            ))}
            </div>
            <button className="add-question" type="button" onClick={addQuestion}>+ Add Question</button>
            <button type="submit">Create Quiz</button>
        </form>
        </div>
        </>
    )
}