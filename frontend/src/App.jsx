import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Router>
      <div className="min-h-screen relative">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
        <ToastContainer
          position="top-center"
          autoClose={2500}
          hideProgressBar
          newestOnTop
          closeOnClick
          pauseOnFocusLoss={false}
          draggable
          pauseOnHover
          theme="dark"
          toastClassName="frosted-glass rounded-2xl border border-charcoal-700"
          bodyClassName="text-slate-300 text-sm font-medium"
        />
      </div>
    </Router>
  )
}

export default App
