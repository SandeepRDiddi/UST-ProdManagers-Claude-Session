import React, { useEffect, useMemo, useState } from 'react'
import { api } from '../api.js'

export default function ProductCatalog({ cart, onAdd, onGoToCart }) {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeCategory, setActiveCategory] = useState('all')

  useEffect(() => {
    Promise.all([api.listProducts(), api.listCategories()])
      .then(([p, c]) => { setProducts(p); setCategories(c) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const categoryName = (id) => categories.find((c) => c.id === id)?.name || id

  const filtered = useMemo(() => {
    if (activeCategory === 'all') return products
    return products.filter((p) => p.category_id === activeCategory)
  }, [products, activeCategory])

  if (loading) return <div className="loading">Loading catalog from the FastAPI backend&hellip;</div>
  if (error) return <ApiErrorHint message={error} />

  return (
    <div>
      <div className="panel" style={{ marginBottom: 18 }}>
        <p className="section-title">Catalog</p>
        <p className="section-desc">
          Products come from the <code>CatalogService</code> application service,
          which reads through the <code>ProductRepository</code> and{' '}
          <code>InventoryRepository</code> ports.
        </p>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          <CategoryChip id="all" label="All" active={activeCategory === 'all'} onClick={setActiveCategory} />
          {categories.map((c) => (
            <CategoryChip key={c.id} id={c.id} label={c.name} active={activeCategory === c.id} onClick={setActiveCategory} />
          ))}
        </div>
      </div>

      <div className="product-grid">
        {filtered.map((p) => (
          <ProductCard key={p.id} product={p} categoryName={categoryName(p.category_id)} inCart={cart[p.id]?.quantity || 0} onAdd={onAdd} />
        ))}
      </div>

      {Object.keys(cart).length > 0 && (
        <div style={{ position: 'fixed', bottom: 22, right: 22 }}>
          <button className="btn btn-amber" onClick={onGoToCart}>
            View cart &rarr;
          </button>
        </div>
      )}
    </div>
  )
}

function CategoryChip({ id, label, active, onClick }) {
  return (
    <button
      onClick={() => onClick(id)}
      className="btn btn-sm"
      style={{
        background: active ? 'var(--teal)' : 'var(--panel)',
        color: active ? '#fff' : 'var(--ink-soft)',
        borderColor: active ? 'var(--teal-deep)' : 'var(--line)',
      }}
    >
      {label}
    </button>
  )
}

function ProductCard({ product, categoryName, inCart, onAdd }) {
  const low = product.quantity_available <= 5
  return (
    <div className="product-card">
      <span className="cat-label">{categoryName}</span>
      <h3>{product.name}</h3>
      <span className="sku">{product.sku}</span>
      <p className="desc">{product.description}</p>
      <span className={`stock-note ${low ? 'low' : ''}`}>
        {product.quantity_available} in stock{low ? ' — low' : ''}
      </span>
      <div className="price-row">
        <span className="price-tag">${product.price.amount.toFixed(2)}</span>
        <button className="btn btn-amber btn-sm" onClick={() => onAdd(product)}>
          {inCart > 0 ? `Add (${inCart} in cart)` : 'Add to cart'}
        </button>
      </div>
    </div>
  )
}

export function ApiErrorHint({ message }) {
  return (
    <div className="error-block">
      <p>Couldn't reach the backend: {message}</p>
      <p style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
        Make sure the FastAPI server is running: <code>uvicorn app.main:app --reload --port 8000</code>
      </p>
    </div>
  )
}
