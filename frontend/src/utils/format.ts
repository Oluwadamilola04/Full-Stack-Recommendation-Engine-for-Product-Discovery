export function formatPrice(price?: number | null) {
  return typeof price === 'number'
    ? new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: 'NGN',
        maximumFractionDigits: 0,
      }).format(price)
    : 'Price unavailable'
}

export function formatRating(rating: number, reviewCount: number) {
  return `★ ${rating.toFixed(1)} (${reviewCount})`
}
