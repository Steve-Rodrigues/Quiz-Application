import { Routes, Route } from 'react-router-dom'
import { Login } from './Login.jsx'
import { Signup } from './Signup.jsx'
import { NotFound } from './NotFound.jsx'
import { MyQuizzes } from './MyQuizzes.jsx'
import { CreateQuizzes } from './CreateQuiz.jsx'
import { EditQuiz } from './EditQuiz.jsx'
import { QuizDashboard } from './QuizDashboard.jsx'
import { TakeQuiz } from './TakeQuiz.jsx'
import { OwnerLayout } from './OwnerLayout.jsx'
import { EditLayout } from './EditLayout.jsx'

function App() {

  return(
    <>
    <Routes>
      <Route path='/' element={<Signup/>}/>
      <Route element={<OwnerLayout/>}>
      <Route path='/quizzes' element={<MyQuizzes/>}/>
      <Route path='/quizzes/new' element={<CreateQuizzes/>}/>
      <Route path='/quizzes/:quizId/dashboard' element={<QuizDashboard/>}/>
      </Route>
      <Route element={<EditLayout/>}>
      <Route path='/quizzes/:quizId/edit' element={<EditQuiz/>}/>
      </Route>
      <Route path='/login' element={<Login/>}/>
      <Route path='/signup' element={<Signup/>}/>
      <Route path='/take/:link' element={<TakeQuiz/>}/>
      <Route path='*' element={<NotFound/>}/>
    </Routes>
    </>
  )
}

export default App
