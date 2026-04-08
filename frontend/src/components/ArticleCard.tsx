import { useState } from 'react'
import type { Article } from '../types'
import { toggleLike } from '../api/articles'
import LikeButton from './LikeButton'

interface Props {
  article: Article
  onArticleUpdate: (updated: Article) => void
  onSelect: (id: number) => void
}

function ArticleCard({ article, onArticleUpdate, onSelect }: Props) {
  const [liking, setLiking] = useState(false)

  async function handleLike() {
    setLiking(true)
    try {
      const result = await toggleLike(article.id, article.liked_by_user)
      onArticleUpdate({ ...article, liked_by_user: result.liked_by_user, like_count: result.like_count })
    } catch (err) {
      console.error('Like failed:', err)
    } finally {
      setLiking(false)
    }
  }

  return (
    <div className="card mb-3 shadow-sm">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start gap-2">
          <h5
            className="card-title mb-1"
            style={{ cursor: 'pointer' }}
            onClick={() => onSelect(article.id)}
          >
            {article.title ?? 'Untitled'}
          </h5>
          <LikeButton
            liked={article.liked_by_user}
            likeCount={article.like_count}
            loading={liking}
            onToggle={handleLike}
          />
        </div>

        {article.summary && (
          <p className="card-text text-muted small mt-1">{article.summary}</p>
        )}

        <div className="d-flex gap-2 flex-wrap mt-2">
          {article.commodity_group && (
            <span className="badge bg-primary">{article.commodity_group}</span>
          )}
          {article.commodity_classification && (
            <span className="badge bg-secondary">{article.commodity_classification}</span>
          )}
          {article.commodity_name && (
            <span className="badge bg-info text-dark">{article.commodity_name}</span>
          )}
        </div>

        <div className="d-flex justify-content-between align-items-center mt-2">
          {article.published_at && (
            <small className="text-muted">
              {new Date(article.published_at).toLocaleString('en-GB', {
                day: 'numeric', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
              })}
            </small>
          )}
          {article.url && (
            <a
              href={article.url}
              target="_blank"
              rel="noreferrer"
              className="small text-truncate"
              style={{ maxWidth: '260px' }}
              title={article.url}
              onClick={e => e.stopPropagation()}
            >
              {new URL(article.url).hostname.replace('www.', '')} ↗
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

export default ArticleCard
