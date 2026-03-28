import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ProductPage from './pages/ProductPage'
import RecommendationsPage from './pages/RecommendationsPage'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/product/:id" element={<ProductPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
