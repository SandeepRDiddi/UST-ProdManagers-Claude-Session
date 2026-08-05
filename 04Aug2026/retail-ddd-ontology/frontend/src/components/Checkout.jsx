import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Checkout({ cart, setQuantity, onOrderPlaced, onBackToCatalog }) {
  const [customers, setCustomers] = useState([])
  const [customerId, setCustomerId] = useState('')
  const [newCustomerName, setNewCustomerName] = useState('')
  const [newCustomerEmail, setNewCustomerEmail] = useState('')
  const [creatingNew, setCreatingNew] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.listCustomers().then((cs) => {
      setCustomers(cs)
      if (cs.length) setCustomerId(cs[0].id)
    })
  }, [])

  const lines = Object.values(cart)
  const total = lines.reduce((sum, l) => sum + l.product.price.amount * l.quantity, 0)

  const handlePlaceOrder = async () => {
    setError(null)
    setSubmitting(true)
    try {
      let finalCustomerId = customerId
      if (creatingNew) {
        const created = await api.createCustomer({ name: newCustomerName, email: newCustomerEmail })
        finalCustomerId = created.id
      }
      const order = await api.placeOrder({
        customer_id: finalCustomerId,
        line_items: lines.map((l) => ({ product_id: l.product.id, quantity: l.quantity })),
      })
      onOrderPlaced(order)
    } catch (e) {
      setError(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="two-col">
      <div className="panel">
        <p className="section-title">Cart</p>
        <p className="section-desc">
          Placing the order calls <code>OrderService.place_order</code>, which
          reserves stock through <code>InventoryService</code> before the{' '}
          <code>Order</code> aggregate is allowed to transition to{' '}
          <code>PLACED</code>.
        </p>

        {lines.length === 0 ? (
          <div className="empty-state">
            Your cart is empty.
            <div style={{ marginTop: 10 }}>
              <button className="btn btn-outline btn-sm" onClick={onBackToCatalog}>
                Browse products
              </button>
            </div>
          </div>
        ) : (
          <>
            {lines.map((l) => (
              <div className="cart-line" key={l.product.id}>
                <div>
                  <div className="name">{l.product.name}</div>
                  <div className="meta">{l.product.sku} · ${l.product.price.amount.toFixed(2)} ea</div>
                </div>
                <div className="qty-control">
                  <button onClick={() => setQuantity(l.product.id, l.quantity - 1)}>−</button>
                  <span>{l.quantity}</span>
                  <button onClick={() => setQuantity(l.product.id, l.quantity + 1)}>+</button>
                </div>
              </div>
            ))}
            <div className="cart-total-row">
              <span className="label">Order total</span>
              <span className="value">${total.toFixed(2)}</span>
            </div>
          </>
        )}
      </div>

      <div className="panel sticky">
        <p className="section-title">Customer</p>
        <p className="section-desc">Who is placing this order?</p>

        {!creatingNew ? (
          <>
            <div className="field">
              <label>Existing customer</label>
              <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>{c.name} ({c.email})</option>
                ))}
              </select>
            </div>
            <button className="btn btn-outline btn-sm" onClick={() => setCreatingNew(true)}>
              + New customer instead
            </button>
          </>
        ) : (
          <>
            <div className="field">
              <label>Name</label>
              <input value={newCustomerName} onChange={(e) => setNewCustomerName(e.target.value)} placeholder="Jane Doe" />
            </div>
            <div className="field">
              <label>Email</label>
              <input value={newCustomerEmail} onChange={(e) => setNewCustomerEmail(e.target.value)} placeholder="jane@example.com" />
            </div>
            <button className="btn btn-outline btn-sm" onClick={() => setCreatingNew(false)}>
              Use existing customer instead
            </button>
          </>
        )}

        {error && <div className="alert error" style={{ marginTop: 14 }}>{error}</div>}

        <button
          className="btn btn-amber btn-block"
          style={{ marginTop: 16 }}
          disabled={lines.length === 0 || submitting || (creatingNew && (!newCustomerName || !newCustomerEmail))}
          onClick={handlePlaceOrder}
        >
          {submitting ? 'Placing order…' : `Place order — $${total.toFixed(2)}`}
        </button>
      </div>
    </div>
  )
}
