import React, { useState } from 'react'
import ProductCatalog from './components/ProductCatalog.jsx'
import Checkout from './components/Checkout.jsx'
import OrderConfirmation from './components/OrderConfirmation.jsx'
import OntologyView from './components/OntologyView.jsx'
import OrderHistory from './components/OrderHistory.jsx'

export default function App() {
  const [tab, setTab] = useState('catalog')
  const [cart, setCart] = useState({}) // { productId: { product, quantity } }
  const [lastOrder, setLastOrder] = useState(null)

  const addToCart = (product) => {
    setCart((prev) => {
      const existing = prev[product.id]
      const quantity = (existing?.quantity || 0) + 1
      return { ...prev, [product.id]: { product, quantity } }
    })
  }

  const setQuantity = (productId, quantity) => {
    setCart((prev) => {
      if (quantity <= 0) {
        const next = { ...prev }
        delete next[productId]
        return next
      }
      return { ...prev, [productId]: { ...prev[productId], quantity } }
    })
  }

  const clearCart = () => setCart({})

  const cartCount = Object.values(cart).reduce((sum, l) => sum + l.quantity, 0)

  const goToOrderConfirmation = (order) => {
    setLastOrder(order)
    clearCart()
    setTab('confirmation')
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <h1>Retail // DDD + Ontology</h1>
          <span className="brand-tag">localhost:5173 → :8000</span>
        </div>
        <p className="subtitle">
          A minimal end-to-end retail app that pairs a Domain-Driven Design
          backend with a parallel ontology (RDF/OWL) describing the same
          concepts &mdash; built to be read, not just run.
        </p>
      </header>

      <nav className="tabs">
        <TabButton id="catalog" tab={tab} setTab={setTab} label="Catalog" />
        <TabButton id="checkout" tab={tab} setTab={setTab} label="Cart & Checkout">
          {cartCount > 0 && <span className="badge-count">{cartCount}</span>}
        </TabButton>
        <TabButton id="orders" tab={tab} setTab={setTab} label="Orders" />
        <TabButton id="ontology" tab={tab} setTab={setTab} label="Ontology" ontology />
      </nav>

      {tab === 'catalog' && <ProductCatalog cart={cart} onAdd={addToCart} onGoToCart={() => setTab('checkout')} />}
      {tab === 'checkout' && (
        <Checkout
          cart={cart}
          setQuantity={setQuantity}
          onOrderPlaced={goToOrderConfirmation}
          onBackToCatalog={() => setTab('catalog')}
        />
      )}
      {tab === 'confirmation' && lastOrder && (
        <OrderConfirmation order={lastOrder} onBackToCatalog={() => setTab('catalog')} />
      )}
      {tab === 'orders' && <OrderHistory />}
      {tab === 'ontology' && <OntologyView />}
    </div>
  )
}

function TabButton({ id, tab, setTab, label, ontology, children }) {
  return (
    <button
      className={`tab-btn ${ontology ? 'tab-ontology' : ''} ${tab === id ? 'active' : ''}`}
      onClick={() => setTab(id)}
    >
      <span className="dot" />
      {label}
      {children}
    </button>
  )
}
