import { useState, useEffect } from 'react';
import { useParams, useNavigate, useOutletContext, Link } from 'react-router-dom';
import { fetchApi } from '../api.js';
import { Loading } from './Loading.jsx';

export function EditQuiz(){
    const { quizId } = useParams();
    const navigate = useNavigate();
    const { setActions } = useOutletContext();

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [publishing, setPublishing] = useState(false);
    const [shareLink, setShareLink] = useState('');
    const [copied, setCopied] = useState(false);
    const [problems, setProblems] = useState([]);

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

    //the layout draws Save Changes/Publish Quiz in the nav-- give it handlers that
    //close over the current form state, and nothing once the quiz is published
    useEffect(() => {
        setActions(shareLink ? null : {
            onSave: handleSubmit,
            onPublish: handlePublish,
            busy: publishing
        });
        return () => setActions(null);
    }, [title, description, questions, publishing, shareLink]);

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

    //shared by Save Changes and Publish-- the backend rejects a PATCH once a quiz is
    //published, so publishing has to save the pending edits before it flips the flag
    function saveQuiz(){
        const cleanQuestions = questions.map(q => ({
            prompt: q.prompt,
            answers: q.answers.map(a => ({ text: a.text, isCorrect: a.isCorrect }))
        }));
        const quiz = { title, description, questions: cleanQuestions };
        return fetchApi(`/api/quizzes/${quizId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(quiz)
        });
    }

    async function handleSubmit(e){
        //no event when the nav button in the layout is the one calling
        if(e) e.preventDefault();
        try{
            await saveQuiz();
            navigate('/quizzes');
        }
        catch(err){
            setError(err.message);
        }
    }

    //mirrors the backend publish rules so the user gets told which question is the
    //problem instead of one generic message for the whole quiz
    function publishProblems(){
        const found = [];
        if(questions.length < 1) found.push('Add at least 1 question.');
        questions.forEach((q, i) => {
            if(q.answers.length < 2) found.push(`Question ${i + 1} needs at least 2 answers.`);
            if(q.answers.filter(a => a.isCorrect).length !== 1)
                found.push(`Question ${i + 1} needs exactly 1 answer ticked as correct.`);
        });
        return found;
    }

    async function handlePublish(){
        const found = publishProblems();
        setProblems(found);
        if(found.length > 0) return;

        //publishing is one way-- the quiz can not be edited or deleted afterwards
        if(!window.confirm('Publish this quiz? You will not be able to edit or delete it afterwards.')) return;
        setError('');
        setProblems([]);
        setPublishing(true);
        try{
            await saveQuiz();
            const published = await fetchApi(`/api/quizzes/${quizId}/publish`, { method: 'POST' });
            setShareLink(`${window.location.origin}/take/${published.share_link}`);
        }
        catch(err){
            setError(err.message);
        }
        finally{
            setPublishing(false);
        }
    }

    async function copyLink(){
        try{
            await navigator.clipboard.writeText(shareLink);
            setCopied(true);
        }
        catch{
            setCopied(false);//clipboard is blocked outside https, the input is there to copy by hand
        }
    }

    if (loading) return <Loading label="Loading quiz" />;

    //once published the form is gone-- nothing on it can be changed anymore
    if (shareLink) {
        return(
            <div className="create-Container">
                <h2 className="createHeader">Quiz Published</h2>
                <p className="text-muted">Share this link with anyone you want to take the quiz.</p>
                <div className="share-row">
                    <input className="share-input" type="text" readOnly value={shareLink}
                        onFocus={(e) => e.target.select()} />
                    <button type="button" className="copy-btn" onClick={copyLink}>
                        {copied ? 'Copied' : 'Copy'}
                    </button>
                </div>
                <Link to="/quizzes" className="link-inline">Back to My Quizzes</Link>
            </div>
        )
    }

    return(
        <>
        <div className="create-Container">
        <form onSubmit={handleSubmit}>
            <label>Quiz Title</label>
            <input className="title-input" type="text" value={title} onChange={handleTitleChange} />
            <label>Description</label>
            <textarea value={description} onChange={handleDescChange} />

            <div className='line-seperate'></div>
            <h2 className='createHeader'>Questions</h2>
            <div className="questions-container">
            {questions.map((q,index) => (
                <div key={q.id} className='question'>
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
                            <input className="quizCheck" type="checkbox" checked={a.isCorrect}
                                onChange={() => toggleCorrect(q.id, a.id)} />
                            <button type="button" className="remove-answer"
                                aria-label="Remove answer"
                                onClick={() => removeAnswer(q.id, a.id)}>&times;</button>
                        </div>
                    ))}</div>
                    <button type="button" className="answer-btn" onClick={() => addAnswer(q.id)}>+ Add Answer</button>
                </div>
            ))}
            </div>
            <button className="add-question" type="button" onClick={addQuestion}>+ Add Question</button>
            {error && <p className="form-error">{error}</p>}
            {problems.length > 0 &&
                <ul className="form-error">
                    {problems.map(p => <li key={p}>{p}</li>)}
                </ul>
            }
        </form>
        </div>
        </>
    )
}
