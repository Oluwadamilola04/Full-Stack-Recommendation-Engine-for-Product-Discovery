export interface Product {
  id: number
  name: string
  description?: string | null
  category: string
  category_raw?: string | null
  brand?: string | null
  price?: number | null
  average_rating: number
  review_count: number
  image_urls?: string[] | null
  tags?: string[] | null
}

export interface Recommendation {
  product_id: number
  score: number
  reason: string
}
