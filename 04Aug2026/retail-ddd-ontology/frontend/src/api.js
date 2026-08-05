const BASE_URL = 'http://localhost:8000/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const message = data?.detail?.message || data?.detail || 'Request failed'
    const err = new Error(typeof message === 'string' ? message : JSON.stringify(message))
    err.details = data?.detail?.items || []
    throw err
  }
  return data
}

export const api = {
  listProducts: () => request('/products'),
  listCategories: () => request('/categories'),
  listCustomers: () => request('/customers'),
  createCustomer: (payload) => request('/customers', { method: 'POST', body: JSON.stringify(payload) }),
  placeOrder: (payload) => request('/orders', { method: 'POST', body: JSON.stringify(payload) }),
  listOrders: () => request('/orders'),
  getOrder: (id) => request(`/orders/${id}`),
  ontologySchema: () => request('/ontology/schema'),
  ontologyGraph: () => request('/ontology/graph'),
  queryProductsInCategory: (categoryId) => request(`/ontology/query/products-in-category/${categoryId}`),
}
