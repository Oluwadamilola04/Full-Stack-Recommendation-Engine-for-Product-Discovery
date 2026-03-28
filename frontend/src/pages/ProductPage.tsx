import { useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import api from '../services/api'
import type { Product } from '../types'
import { formatPrice } from '../utils/format'

export default function ProductPage() {
  const { id } = useParams<{ id: string }>()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchProduct = async () => {
      if (!id) {
        setError('Missing product id')
        setLoading(false)
        return
      }

      try {
        const response = await api.get(`/products/${id}`)
        setProduct(response.data)
      } catch (err: any) {
        const detail = err?.response?.data?.detail
        setError(detail || err.message || 'Failed to load product')
      } finally {
        setLoading(false)
      }
    }

    fetchProduct()
  }, [id])

  if (loading) return <div className="loading">Loading product...</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!product) return <div className="error">Product not found</div>

  return (
    <div className="product-page">
      <div className="product-detail">
        <h1>{product.name}</h1>
        {product.brand ? <p className="brand">{product.brand}</p> : null}
        <p className={`price${typeof product.price === 'number' ? '' : ' muted'}`}>
          {typeof product.price === 'number'
            ? `${formatPrice(product.price)} estimated`
            : formatPrice(product.price)}
        </p>
        <p className="rating">
          ★ {product.average_rating.toFixed(1)} ({product.review_count} reviews)
        </p>
        <p className="category">Category: {product.category}</p>
        {product.image_urls?.[0] ? (
          <img className="product-hero-image" src={product.image_urls[0]} alt={product.name} />
        ) : null}
        {product.tags?.length ? (
          <div className="tags">
            {product.tags.slice(0, 10).map((tag) => (
              <span key={tag} className="tag">
                {tag}
              </span>
            ))}
          </div>
        ) : null}
        {product.description ? <p className="description">{product.description}</p> : null}
        <button type="button">Add to Cart</button>
      </div>
    </div>
  )
}
