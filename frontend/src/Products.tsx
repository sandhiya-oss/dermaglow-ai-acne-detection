import { useState } from 'react'

type Product = {
  name: string
  category: string
  description: string
  detail: string
  icon: string
}

const products: Product[] = [
  {
    name: 'Gentle Gel Cleanser',
    category: 'Cleansers',
    description: 'A simple first step for daily cleansing.',
    detail: 'Look for a gentle, non-abrasive formula.',
    icon: '◉',
  },
  {
    name: 'Hydrating Cleanser',
    category: 'Cleansers',
    description: 'Designed to cleanse without excessive dryness.',
    detail: 'Consider fragrance-free options if your skin is sensitive.',
    icon: '❋',
  },
  {
    name: 'Lightweight Moisturizer',
    category: 'Moisturizers',
    description: 'Helps support the skin moisture barrier.',
    detail: 'Look for non-comedogenic products if you are acne-prone.',
    icon: '♡',
  },
  {
    name: 'Barrier Support Cream',
    category: 'Moisturizers',
    description: 'A moisturizer option for dry-feeling skin.',
    detail: 'Choose a texture that feels comfortable on your skin.',
    icon: '✿',
  },
  {
    name: 'Daily Broad-Spectrum SPF',
    category: 'Sun Protection',
    description: 'Daily protection against UVA and UVB rays.',
    detail: 'Choose broad-spectrum SPF 30 or higher and reapply as directed.',
    icon: '☼',
  },
  {
    name: 'Sensitive Skin Sunscreen',
    category: 'Sun Protection',
    description: 'An option to explore for a sensitive-skin routine.',
    detail: 'Patch test new products and follow the product label.',
    icon: '☀',
  },
]

const categories = [
  'All',
  'Cleansers',
  'Moisturizers',
  'Sun Protection',
]

export default function Products() {
  const [category, setCategory] = useState('All')
  const [search, setSearch] = useState('')
  const [saved, setSaved] = useState<string[]>([])

  const visibleProducts = products.filter((product) => {
    const matchesCategory =
      category === 'All' || product.category === category
    const query = search.toLowerCase().trim()
    const matchesSearch =
      product.name.toLowerCase().includes(query) ||
      product.description.toLowerCase().includes(query) ||
      product.category.toLowerCase().includes(query)

    return matchesCategory && matchesSearch
  })

  function toggleSaved(name: string) {
    setSaved((current) =>
      current.includes(name)
        ? current.filter((item) => item !== name)
        : [...current, name]
    )
  }

  return (
    <section className="products-page">
      <p className="eyebrow">YOUR SKINCARE LIBRARY</p>
      <h2 className="progress-title">Find your everyday essentials.</h2>
      <p className="progress-intro">
        Explore skincare categories and learn what to look for.
        These are product types, not specific brand endorsements.
      </p>

      <div className="product-search-wrap">
        <span>⌕</span>
        <input
          aria-label="Search skincare products"
          placeholder="Search cleansers, moisturizers, sunscreen..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      <div className="product-filters" aria-label="Product categories">
        {categories.map((item) => (
          <button
            key={item}
            className={`product-filter ${category === item ? 'active-filter' : ''}`}
            onClick={() => setCategory(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="product-results-heading">
        <div>
          <h3>Explore the collection</h3>
          <p>{visibleProducts.length} product types</p>
        </div>
        <span>{saved.length} saved</span>
      </div>

      {visibleProducts.length === 0 ? (
        <div className="product-empty">
          No matches found. Try another search or category.
        </div>
      ) : (
        <div className="product-grid">
          {visibleProducts.map((product, index) => (
            <article className="product-card" key={product.name}>
              <div className={`product-art product-art-${index % 4}`}>
                <span className="product-art-icon">{product.icon}</span>
                <span className="product-art-label">
                  {product.category.toUpperCase()}
                </span>
              </div>

              <div className="product-card-body">
                <p className="product-category">{product.category}</p>
                <h4>{product.name}</h4>
                <p className="product-description">{product.description}</p>
                <p className="product-detail">{product.detail}</p>
                <button
                  className="product-save"
                  onClick={() => toggleSaved(product.name)}
                >
                  {saved.includes(product.name) ? '♥ Saved' : '♡ Save item'}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      <div className="product-note">
        <span>✿</span>
        <p>
          <strong>A gentle reminder</strong><br />
          Introduce new products gradually. Product suitability varies;
          this library does not diagnose skin conditions or replace
          professional advice.
        </p>
      </div>
    </section>
  )
}
