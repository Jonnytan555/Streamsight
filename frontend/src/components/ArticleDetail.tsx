import { useState, useEffect } from 'react'
import type { ArticleDetail as ArticleDetailType } from '../types'
import { getArticle, toggleLike } from '../api/articles'

interface Props {
  articleId: number | null
  onClose: () => void
}

function ArticleDetail({ articleId, onClose }: Props) {
  const [article, setArticle] = useState<ArticleDetailType | null>(null)
  const [loading, setLoading] = useState(false)
  const [liking, setLiking] = useState(false)

  useEffect(() => {
    if (articleId === null) return
    setLoading(true)
    setArticle(null)
    getArticle(articleId)
      .then(data => setArticle(data))
      .catch(err => console.error('Failed to load article:', err))
      .finally(() => setLoading(false))
  }, [articleId])

  if (articleId === null) return null

  async function handleLike() {
    if (!article) return
    setLiking(true)
    try {
      const result = await toggleLike(article.id, article.liked_by_user)
      setArticle({ ...article, liked_by_user: result.liked_by_user, like_count: result.like_count })
    } finally {
      setLiking(false)
    }
  }

  return (
    <div
      className="modal d-block"
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
      onClick={onClose}
    >
      <div className="modal-dialog modal-lg modal-dialog-scrollable" onClick={e => e.stopPropagation()}>
        <div className="modal-content">

          <div className="modal-header">
            <h5 className="modal-title">{loading ? 'Loading…' : (article?.title ?? 'Article')}</h5>
            <button className="btn-close" onClick={onClose} aria-label="Close" />
          </div>

          <div className="modal-body">
            {loading && (
              <div className="text-center py-4">
                <div className="spinner-border text-primary" role="status" />
              </div>
            )}

            {article && (
              <>
                <div className="d-flex gap-2 flex-wrap mb-3">
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

                {article.summary && (
                  <p className="lead">{article.summary}</p>
                )}

                <table className="table table-sm table-borderless mt-3">
                  <tbody>
                    {article.published_at && (
                      <tr>
                        <th scope="row" style={{ width: '160px' }}>Published</th>
                        <td>{new Date(article.published_at).toLocaleDateString('en-GB', {
                          day: 'numeric', month: 'long', year: 'numeric'
                        })}</td>
                      </tr>
                    )}
                    {article.source_name && (
                      <tr>
                        <th scope="row">Source</th>
                        <td>{article.source_name}</td>
                      </tr>
                    )}
                  </tbody>
                </table>

                {article.url && (
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-outline-primary btn-sm"
                  >
                    Read original source ↗
                  </a>
                )}
              </>
            )}
          </div>

          <div className="modal-footer">
            {article && (
              <button
                className={`btn ${article.liked_by_user ? 'btn-danger' : 'btn-outline-danger'}`}
                onClick={handleLike}
                disabled={liking}
              >
                {article.liked_by_user ? '♥ Liked' : '♡ Like'} ({article.like_count})
              </button>
            )}
            <button className="btn btn-secondary" onClick={onClose}>Close</button>
          </div>

        </div>
      </div>
    </div>
  )
}

export default ArticleDetail
