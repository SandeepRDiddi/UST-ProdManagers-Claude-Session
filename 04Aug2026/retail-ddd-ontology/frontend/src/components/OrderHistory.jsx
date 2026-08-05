import React, { useEffect, useState } from 'react'
import { api } from '../api.js'
import { ApiErrorHint } from './ProductCatalog.jsx'

export default function OrderHistory() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.listOrders().then(setOrders).catch((e) => setError(e.message)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading">Loading orders…</div>
  if (error) return <ApiErrorHint message={error} />

  return (
    <div className="panel">
      <p className="section-title">Orders</p>
      <p className="section-desc">
        Every placed order lives in the in-memory <code>OrderRepository</code>{' '}
        for this server session. Restarting the backend resets it.
      </p>

      {orders.length === 0 ? (
        <div className="empty-state">No orders yet — place one from the Catalog tab.</div>
      ) : (
        <table className="order-table">
          <thead>
            <tr>
              <th>Order</th>
              <th>Customer</th>
              <th>Status</th>
              <th>Items</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>#{o.id}</td>
                <td>{o.customer_id}</td>
                <td>{o.status}</td>
                <td>{o.lines.length}</td>
                <td>${o.total.amount.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
