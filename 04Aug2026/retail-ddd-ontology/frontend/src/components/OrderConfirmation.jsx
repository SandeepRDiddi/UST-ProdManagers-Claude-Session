import React from 'react'

export default function OrderConfirmation({ order, onBackToCatalog }) {
  return (
    <div className="panel" style={{ maxWidth: 640, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <p className="section-title">Order placed</p>
        <span className="order-id-chip">#{order.id}</span>
      </div>
      <p className="section-desc">
        Status: <strong>{order.status}</strong> · Placed at {new Date(order.placed_at).toLocaleString()}
      </p>

      <table className="order-table">
        <thead>
          <tr>
            <th>Item</th>
            <th>SKU</th>
            <th>Qty</th>
            <th>Line total</th>
          </tr>
        </thead>
        <tbody>
          {order.lines.map((l) => (
            <tr key={l.product_id}>
              <td className="name-cell">{l.product_name}</td>
              <td>{l.sku}</td>
              <td>{l.quantity}</td>
              <td>${l.line_total.amount.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="cart-total-row">
        <span className="label">Total</span>
        <span className="value">${order.total.amount.toFixed(2)}</span>
      </div>

      <button className="btn btn-amber" style={{ marginTop: 18 }} onClick={onBackToCatalog}>
        Back to catalog
      </button>
    </div>
  )
}
