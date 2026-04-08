export interface Article {
  id: number
  title: string | null
  summary: string | null
  commodity_group: string | null
  commodity_classification: string | null
  commodity_name: string | null
  published_at: string | null
  url: string | null
  like_count: number
  liked_by_user: boolean
}

export interface ArticleDetail extends Article {
  source_type: string | null
  source_name: string | null
}

export interface FilterOptions {
  commodity_groups: string[]
  commodity_classifications: string[]
}

export interface LikeResponse {
  article_id: number
  liked: boolean
  like_count: number
  liked_by_user: boolean
}
