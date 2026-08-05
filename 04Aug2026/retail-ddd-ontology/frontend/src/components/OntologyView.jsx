import React, { useEffect, useMemo, useState } from 'react'
import { api } from '../api.js'
import { ApiErrorHint } from './ProductCatalog.jsx'

export default function OntologyView() {
  const [view, setView] = useState('schema') // 'schema' | 'instances' | 'query'
  const [schema, setSchema] = useState(null)
  const [instances, setInstances] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([api.ontologySchema(), api.ontologyGraph()])
      .then(([s, i]) => { setSchema(s); setInstances(i) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading">Loading ontology from /api/ontology&hellip;</div>
  if (error) return <ApiErrorHint message={error} />

  return (
    <div>
      <div className="panel" style={{ marginBottom: 18 }}>
        <p className="section-title">Ontology</p>
        <p className="section-desc">
          Alongside the DDD backend, this app maintains an RDF/OWL ontology
          (built with <code>rdflib</code>) describing the same retail world
          in terms of classes and relationships. The <strong>Schema</strong> tab
          is the fixed vocabulary (TBox); <strong>Live data</strong> is that
          vocabulary instantiated from whatever is in the repositories right
          now (ABox); <strong>Query</strong> runs a SPARQL property-path
          query that walks the category is-a hierarchy.
        </p>
        <div className="onto-toggle">
          <button className={view === 'schema' ? 'active' : ''} onClick={() => setView('schema')}>Schema (TBox)</button>
          <button className={view === 'instances' ? 'active' : ''} onClick={() => setView('instances')}>Live data (ABox)</button>
          <button className={view === 'query' ? 'active' : ''} onClick={() => setView('query')}>SPARQL query</button>
        </div>
      </div>

      {view === 'schema' && <SchemaDiagram schema={schema} />}
      {view === 'instances' && <InstanceTriples instances={instances} />}
      {view === 'query' && <SparqlDemo schema={schema} />}
    </div>
  )
}

function SchemaDiagram({ schema }) {
  const width = 640
  const height = 460
  const cx = width / 2
  const cy = height / 2
  const radius = 170

  const positions = useMemo(() => {
    const map = {}
    schema.nodes.forEach((n, i) => {
      const angle = (i / schema.nodes.length) * 2 * Math.PI - Math.PI / 2
      map[n.id] = { x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) }
    })
    return map
  }, [schema])

  return (
    <div className="panel">
      <p className="section-title">Class diagram</p>
      <p className="section-desc">Six OWL classes and the object properties connecting them, straight from <code>ontology/schema.py</code>.</p>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" style={{ maxWidth: 640 }}>
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="var(--teal-deep)" />
          </marker>
        </defs>
        {schema.edges.map((e, i) => {
          if (e.source === e.target) {
            const p = positions[e.source]
            const loopR = 30
            return (
              <g key={i}>
                <path
                  d={`M ${p.x - 6} ${p.y - 22} A ${loopR} ${loopR} 0 1 1 ${p.x + 6} ${p.y - 22}`}
                  fill="none" stroke="var(--teal-deep)" strokeWidth="1.3" markerEnd="url(#arrow)"
                />
                <text x={p.x} y={p.y - 58} textAnchor="middle" className="edge-label" fontFamily="var(--font-mono)" fontSize="10" fill="var(--amber-deep)">
                  {e.label}
                </text>
              </g>
            )
          }
          const s = positions[e.source]
          const t = positions[e.target]
          const mx = (s.x + t.x) / 2
          const my = (s.y + t.y) / 2
          return (
            <g key={i}>
              <line x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="var(--teal-deep)" strokeWidth="1.3" markerEnd="url(#arrow)" opacity="0.75" />
              <rect x={mx - e.label.length * 3} y={my - 9} width={e.label.length * 6} height={14} fill="var(--bg)" opacity="0.9" />
              <text x={mx} y={my + 2} textAnchor="middle" fontFamily="var(--font-mono)" fontSize="10" fill="var(--amber-deep)">{e.label}</text>
            </g>
          )
        })}
        {schema.nodes.map((n) => {
          const p = positions[n.id]
          return (
            <g key={n.id}>
              <rect x={p.x - 52} y={p.y - 16} width="104" height="32" rx="8" fill="var(--panel)" stroke="var(--teal)" strokeWidth="1.4" />
              <text x={p.x} y={p.y + 4} textAnchor="middle" fontFamily="var(--font-display)" fontWeight="600" fontSize="12" fill="var(--ink)">
                {n.label}
              </text>
            </g>
          )
        })}
      </svg>
      <p className="footnote">
        Arrows read subject &rarr; object, e.g. <em>OrderLine forProduct Product</em>.
        The self-loop on Category is <code>subCategoryOf</code>, the relationship a SPARQL
        property path walks transitively in the Query tab.
      </p>
    </div>
  )
}

function InstanceTriples({ instances }) {
  const grouped = useMemo(() => {
    const counts = {}
    instances.nodes.forEach((n) => {
      const type = n.label.includes('/') ? n.label.split('/')[0] : n.group
      counts[type] = (counts[type] || 0) + 1
    })
    return counts
  }, [instances])

  const short = (uri) => (uri.includes('#') ? uri.split('#')[1] : uri)

  return (
    <div className="panel">
      <p className="section-title">Live knowledge graph</p>
      <p className="section-desc">
        {instances.nodes.length} individuals and {instances.edges.length} relationships,
        generated fresh on every request from whatever is currently in the repositories.
      </p>
      <div className="class-legend">
        {Object.entries(grouped).map(([type, count]) => (
          <span className="chip" key={type}>{type} × {count}</span>
        ))}
      </div>
      <div className="triple-list" style={{ marginTop: 14 }}>
        {instances.edges.map((e, i) => (
          <div className="triple" key={i}>
            <span className="subj">{short(e.source)}</span>
            <span className="pred">{e.label}</span>
            <span className="obj">{short(e.target)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function SparqlDemo({ schema }) {
  const [categoryId, setCategoryId] = useState('cat-electronics')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  const runQuery = () => {
    setLoading(true)
    api.queryProductsInCategory(categoryId).then(setResults).finally(() => setLoading(false))
  }

  useEffect(() => { runQuery() }, [])

  return (
    <div className="panel">
      <p className="section-title">SPARQL: products in a category (including subcategories)</p>
      <p className="section-desc">
        This is the payoff of modeling categories as an RDF is-a chain: one
        query, using the <code>subCategoryOf*</code> property path, finds
        products in a category <em>or any of its descendants</em> — no
        recursive SQL needed.
      </p>
      <pre style={{
        background: 'var(--bg)', border: '1px solid var(--line)', borderRadius: 8,
        padding: 12, fontSize: 11.5, fontFamily: 'var(--font-mono)', overflowX: 'auto',
      }}>
{`SELECT ?product ?label ?price WHERE {
  ?product a retail:Product ;
           rdfs:label ?label ;
           retail:hasPrice ?price ;
           retail:belongsToCategory ?cat .
  ?cat retail:subCategoryOf* <...#Category/${categoryId}> .
}`}
      </pre>

      <div className="field" style={{ maxWidth: 260 }}>
        <label>Category</label>
        <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
          <option value="cat-electronics">Electronics (has subcategories)</option>
          <option value="cat-computers">Computers</option>
          <option value="cat-laptops">Laptops</option>
          <option value="cat-audio">Audio</option>
          <option value="cat-kitchen">Kitchen (has subcategories)</option>
          <option value="cat-appliances">Small Appliances</option>
        </select>
      </div>
      <button className="btn btn-teal btn-sm" onClick={runQuery} disabled={loading}>
        {loading ? 'Running…' : 'Run query'}
      </button>

      {results && (
        <table className="order-table" style={{ marginTop: 14 }}>
          <thead><tr><th>Product</th><th>Price</th></tr></thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.product_uri}>
                <td className="name-cell">{r.label}</td>
                <td>${r.price.toFixed(2)}</td>
              </tr>
            ))}
            {results.length === 0 && <tr><td colSpan="2">No products found.</td></tr>}
          </tbody>
        </table>
      )}
    </div>
  )
}
