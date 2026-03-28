import { useState } from 'react'
import api from '../services/api'
import type { Product, Recommendation } from '../types'

export default function RecommendationsPage() {
  const [userId, setUserId] = useState('')
  const [strategy, setStrategy] = useState('hybrid')
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [productsById, setProductsById] = useState<Record<number, Product>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGetRecommendations = async () => {
    if (!userId) {
      setError('Please enter a user ID')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await api.get(`/recommendations/user/${userId}`, {
        params: { strategy, limit: 10 },
      })
      const recs: Recommendation[] = response.data.recommendations
      setRecommendations(recs)

      const productIds = recs.map((recommendation) => recommendation.product_id)
      const results = await Promise.all(
        productIds.map((productId) =>
          api.get(`/products/${productId}`).then((result) => result.data).catch(() => null),
        ),
      )

      const productMap: Record<number, Product> = {}
      for (const product of results) {
        if (product && typeof product.id === 'number') {
          productMap[product.id] = product
        }
      }
      setProductsById(productMap)
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      setError(detail || err.message || 'Failed to load recommendations')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="recommendations-page">
      <h1>Personalized Recommendations</h1>

      <div className="filter-section">
        <input
          type="number"
          placeholder="Enter User ID"
          value={userId}
          onChange={(event) => setUserId(event.target.value)}
        />

        <select value={strategy} onChange={(event) => setStrategy(event.target.value)}>
          <option value="hybrid">Hybrid</option>
          <option value="collaborative">Collaborative Filtering</option>
          <option value="content">Content-Based</option>
        </select>

        <button onClick={handleGetRecommendations} disabled={loading}>
          {loading ? 'Loading...' : 'Get Recommendations'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {recommendations.length > 0 && (
        <div className="recommendations-list">
          <h2>Recommended Products</h2>
          {recommendations.map((recommendation) => (
            <div key={recommendation.product_id} className="recommendation-item">
              {productsById[recommendation.product_id]?.image_urls?.[0] ? (
                <img
                  className="product-image"
                  src={productsById[recommendation.product_id].image_urls![0]}
                  alt={productsById[recommendation.product_id].name}
                />
              ) : (
                <div className="product-image placeholder" />
              )}
              <p className="title">
                {productsById[recommendation.product_id]?.name ||
                  `Product ID: ${recommendation.product_id}`}
              </p>
              <p>Score: {recommendation.score.toFixed(2)}</p>
              <p className="reason">{recommendation.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
