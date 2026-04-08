import api from './client'
import type { Article, ArticleDetail, FilterOptions, LikeResponse } from '../types'

// axios interceptor in client.ts already handles 401 → removeToken automatically

export async function getArticles(params?: Record<string, string>): Promise<Article[]> {
  const res = await api.get('/api/articles', { params })
  return res.data
}

export async function getArticle(id: number): Promise<ArticleDetail> {
  const res = await api.get(`/api/articles/${id}`)
  return res.data
}

export async function getFilterOptions(): Promise<FilterOptions> {
  const res = await api.get('/api/articles/filters')
  return res.data
}

export async function toggleLike(id: number, currentlyLiked: boolean): Promise<LikeResponse> {
  const res = await api.request({
    method: currentlyLiked ? 'DELETE' : 'POST',
    url: `/api/articles/${id}/like`,
  })
  return res.data
}
