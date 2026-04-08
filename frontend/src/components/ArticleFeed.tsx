import { useState, useEffect } from 'react'
import type { Article, FilterOptions } from '../types'
import { getArticles, getFilterOptions } from '../api/articles'
import ArticleCard from './ArticleCard'
import FilterBar from './FilterBar'
import type { Filters } from './FilterBar'

const PAGE_SIZE = 20

interface Props {
  onSelectArticle: (id: number) => void
}

function ArticleFeed({ onSelectArticle }: Props) {
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null)
  const [filters, setFilters] = useState<Filters>({ commodity_group: '', commodity_classification: '' })

  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasMore, setHasMore] = useState(true)
  const [skip, setSkip] = useState(0)

  useEffect(() => {
    getFilterOptions().then(setFilterOptions).catch(console.error)
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    setSkip(0)
    setHasMore(true)

    const params: Record<string, string> = { limit: String(PAGE_SIZE), skip: '0' }
    if (filters.commodity_group)          params.commodity_group          = filters.commodity_group
    if (filters.commodity_classification) params.commodity_classification = filters.commodity_classification

    getArticles(params)
      .then(data => {
        setArticles(data)
        setSkip(data.length)
        setHasMore(data.length === PAGE_SIZE)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [filters])

  async function loadMore() {
    setLoadingMore(true)
    try {
      const params: Record<string, string> = { limit: String(PAGE_SIZE), skip: String(skip) }
      if (filters.commodity_group)          params.commodity_group          = filters.commodity_group
      if (filters.commodity_classification) params.commodity_classification = filters.commodity_classification

      const data = await getArticles(params)
      setArticles(prev => [...prev, ...data])
      setSkip(prev => prev + data.length)
      setHasMore(data.length === PAGE_SIZE)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoadingMore(false)
    }
  }

  function updateArticle(updated: Article) {
    setArticles(prev => prev.map(a => a.id === updated.id ? updated : a))
  }

  return (
    <div>
      <FilterBar options={filterOptions} filters={filters} onChange={setFilters} />

      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading…</span>
          </div>
        </div>
      )}

      {error && <div className="alert alert-danger">{error}</div>}

      {!loading && !error && articles.length === 0 && (
        <div className="text-center py-5 text-muted">
          <p className="mb-0">No articles found.</p>
          {(filters.commodity_group || filters.commodity_classification) && (
            <p className="small">Try clearing the filters.</p>
          )}
        </div>
      )}

      {articles.map(article => (
        <ArticleCard
          key={article.id}
          article={article}
          onArticleUpdate={updateArticle}
          onSelect={onSelectArticle}
        />
      ))}

      {!loading && hasMore && (
        <div className="text-center mt-2 mb-4">
          <button
            className="btn btn-outline-primary"
            onClick={loadMore}
            disabled={loadingMore}
          >
            {loadingMore
              ? <><span className="spinner-border spinner-border-sm me-2" />Loading…</>
              : 'Load more'}
          </button>
        </div>
      )}

      {!loading && !hasMore && articles.length > 0 && (
        <p className="text-center text-muted small mb-4">All articles loaded</p>
      )}
    </div>
  )
}

export default ArticleFeed
