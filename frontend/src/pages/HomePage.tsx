import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import type { Product } from '../types'
import { formatPrice, formatRating } from '../utils/format'

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/products/', { params: { limit: 24 } })
        setProducts(response.data)
      } catch (err: any) {
        setError(err.message || 'Failed to load products')
      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [])

  if (loading) return <div className="loading">Loading products...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="home-page">
      <section className="hero">
        <h1>Welcome to RecommendHub</h1>
        <p>Discover products tailored just for you</p>
      </section>

      <section className="products-grid">
        <h2>Featured Products</h2>
        <div className="grid">
          {products.map((product) => (
            <Link key={product.id} to={`/product/${product.id}`} className="product-card">
              {product.image_urls?.[0] ? (
                <img className="product-image" src={product.image_urls[0]} alt={product.name} />
              ) : (
                <div className="product-image placeholder" />
              )}
              <h3>{product.name}</h3>
              {product.brand ? <p className="brand">{product.brand}</p> : null}
              <p className="category">{product.category}</p>
              <p className={`price${typeof product.price === 'number' ? '' : ' muted'}`}>
                {formatPrice(product.price)}
              </p>
              <p className="rating">{formatRating(product.average_rating, product.review_count)}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
