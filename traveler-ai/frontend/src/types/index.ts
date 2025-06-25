// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  role: string
  avatar?: string
  created_at: string
}

export interface UserProfile extends User {
  preferences: {
    default_ai_provider: string
    language: string
    timezone: string
  }
  stats: {
    total_itineraries: number
    favorite_destinations: string[]
    member_since: string
  }
}

// 攻略生成相关类型
export interface ItineraryGenerationRequest {
  destination: string
  days: number
  travel_style?: string
  budget_min?: number
  budget_max?: number
  group_size: number
  start_date?: string
  ai_provider?: string
  special_requirements?: string
}

export interface Itinerary {
  id: number
  title: string
  destination: string
  days: number
  status: 'pending' | 'generating' | 'completed' | 'failed'
  progress: number
  user_id: number
  travel_style?: string
  budget_min?: number
  budget_max?: number
  group_size: number
  start_date?: string
  ai_provider: string
  overview_content?: string
  overview_markdown?: string
  center_latitude?: number
  center_longitude?: number
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface DailyItinerary {
  id: number
  itinerary_id: number
  day_number: number
  date?: string
  title: string
  content: string
  markdown_content: string
}

export interface GenerationProgress {
  itinerary_id: number
  progress: number
  status: string
  message: string
  current_step?: string
}

// AI服务相关类型
export interface AIProvider {
  name: string
  display_name: string
  description: string
  status: 'available' | 'unavailable'
  config: {
    base_url: string
    model: string
    available: boolean
  }
}

export interface AIGenerationRequest {
  prompt: string
  provider?: string
  temperature: number
  max_tokens: number
}

// 地图服务相关类型
export interface Location {
  latitude: number
  longitude: number
  address: string
  formatted_address?: string
  level?: string
  confidence?: number
}

export interface PlaceInfo {
  name: string
  address: string
  latitude?: number
  longitude?: number
  uid?: string
  area?: string
  city?: string
  province?: string
  telephone?: string
  tag?: string
  type?: string
  detail_info?: Record<string, any>
}

export interface PlaceSearchRequest {
  query: string
  region?: string
  location?: string
  radius?: number
  tag?: string
  page_num: number
  page_size: number
}

export interface PlaceSearchResult {
  total: number
  places: PlaceInfo[]
  page_num: number
  page_size: number
}

export interface DirectionsRequest {
  origin: string
  destination: string
  mode: 'driving' | 'riding' | 'walking' | 'transit'
}

export interface DirectionsResult {
  distance: number
  duration: number
  origin: string
  destination: string
  mode: string
  steps: any[]
  polyline: string
  taxi_fee?: Record<string, any>
}

export interface WeatherInfo {
  location: string
  current: {
    text?: string
    temperature?: string
  }
  forecast: Array<{
    date?: string
    text?: string
    low?: string
    high?: string
  }>
  update_time: string
}

// 模板相关类型
export interface Template {
  id: number
  name: string
  type: 'overview' | 'daily'
  description: string
  category: string
  content: string
  variables?: Record<string, any>
  default_values?: Record<string, any>
  is_active: boolean
  is_system: boolean
  created_at: string
  updated_at: string
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message: string
  error?: string
  details?: string
}

export interface PaginatedResponse<T = any> {
  success: boolean
  data: {
    items: T[]
    total: number
    page: number
    page_size: number
    pages: number
  }
  message: string
}

// 统计数据类型
export interface GenerationStats {
  total_itineraries: number
  total_users: number
  popular_destinations: Array<{
    destination: string
    count: number
  }>
  average_days: number
  success_rate: number
  avg_generation_time: number
}

// 表单验证规则类型
export interface FormRule {
  required?: boolean
  message?: string
  trigger?: string | string[]
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
}

// 通用组件Props类型
export interface LoadingState {
  loading: boolean
  text?: string
}

export interface PageMeta {
  title: string
  description?: string
  keywords?: string
}

// 路由相关类型
export interface RouteMenuItem {
  path: string
  name: string
  title: string
  icon?: string
  children?: RouteMenuItem[]
  hidden?: boolean
  roles?: string[]
} 