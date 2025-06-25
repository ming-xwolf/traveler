import { request } from '@/utils/request'
import type {
  Itinerary,
  ItineraryGenerationRequest,
  DailyItinerary,
  GenerationProgress,
  AIProvider,
  AIGenerationRequest,
  Location,
  PlaceSearchRequest,
  PlaceSearchResult,
  DirectionsRequest,
  DirectionsResult,
  WeatherInfo,
  Template,
  User,
  UserProfile,
  PaginatedResponse,
  GenerationStats,
} from '@/types'

// 攻略生成API
export const itineraryApi = {
  // 生成攻略
  generate(data: ItineraryGenerationRequest) {
    return request.post<Itinerary>('/v1/itinerary/generate', data)
  },

  // 查询生成进度
  getProgress(itineraryId: number) {
    return request.get<GenerationProgress>(`/v1/itinerary/progress/${itineraryId}`)
  },

  // 验证目的地
  validateDestination(destination: string) {
    return request.get<{ valid: boolean; location?: Location; suggestions?: string[] }>(
      `/v1/itinerary/validate?destination=${encodeURIComponent(destination)}`
    )
  },

  // 获取攻略详情
  getDetail(itineraryId: number) {
    return request.get<{
      itinerary: Itinerary
      daily_itineraries: DailyItinerary[]
    }>(`/v1/itinerary/${itineraryId}`)
  },

  // 获取用户攻略列表
  getList(params: {
    page?: number
    page_size?: number
    status?: string
    destination?: string
  } = {}) {
    return request.get<PaginatedResponse<Itinerary>>('/v1/itinerary/list', { params })
  },

  // 删除攻略
  delete(itineraryId: number) {
    return request.delete(`/v1/itinerary/${itineraryId}`)
  },

  // 导出攻略
  export(itineraryId: number, format: 'markdown' | 'html' | 'pdf') {
    return request.download(`/v1/itinerary/${itineraryId}/export?format=${format}`)
  },

  // 获取模板列表
  getTemplates(type?: 'overview' | 'daily') {
    return request.get<Template[]>('/v1/itinerary/templates', {
      params: type ? { type } : undefined
    })
  },

  // 获取示例攻略
  getExamples() {
    return request.get<{
      overview: string
      daily_samples: Array<{ day: number; content: string }>
    }>('/v1/itinerary/examples')
  },
}

// AI服务API
export const aiApi = {
  // 获取可用的AI服务商
  getProviders() {
    return request.get<AIProvider[]>('/v1/ai/providers')
  },

  // 测试AI连接
  testConnection(provider: string) {
    return request.post<{ status: 'success' | 'failed'; message: string }>('/v1/ai/test', {
      provider
    })
  },

  // 直接生成文本
  generate(data: AIGenerationRequest) {
    return request.post<{ text: string; usage?: any }>('/v1/ai/generate', data)
  },
}

// 地图服务API
export const mapsApi = {
  // 地理编码
  geocode(address: string) {
    return request.post<Location>('/v1/maps/geocode', { address })
  },

  // 逆地理编码
  reverseGeocode(latitude: number, longitude: number) {
    return request.post<{
      formatted_address: string
      location: Location
      address_components: any
    }>('/v1/maps/reverse-geocode', { latitude, longitude })
  },

  // 搜索地点
  searchPlaces(data: PlaceSearchRequest) {
    return request.post<PlaceSearchResult>('/v1/maps/search-places', data)
  },

  // 获取地点详情
  getPlaceDetails(uid: string) {
    return request.get<any>(`/v1/maps/place-details/${uid}`)
  },

  // 路线规划
  getDirections(data: DirectionsRequest) {
    return request.post<DirectionsResult>('/v1/maps/directions', data)
  },

  // 批量算路
  getDistanceMatrix(origins: string[], destinations: string[], mode: string = 'driving') {
    return request.post<{
      origins: string[]
      destinations: string[]
      rows: Array<{
        elements: Array<{
          status: string
          distance?: { text: string; value: number }
          duration?: { text: string; value: number }
        }>
      }>
    }>('/v1/maps/distance-matrix', { origins, destinations, mode })
  },

  // 获取天气信息
  getWeather(location?: string, districtId?: number) {
    return request.get<WeatherInfo>('/v1/maps/weather', {
      params: { location, district_id: districtId }
    })
  },

  // IP定位
  getIpLocation(ip?: string) {
    return request.get<{
      ip: string
      location: Location
      isp: string
    }>('/v1/maps/ip-location', {
      params: ip ? { ip } : undefined
    })
  },
}

// 用户认证API
export const authApi = {
  // 登录
  login(username: string, password: string) {
    return request.post<{
      access_token: string
      token_type: string
      user: User
    }>('/v1/auth/login', { username, password })
  },

  // 注册
  register(data: {
    username: string
    email: string
    password: string
    full_name?: string
  }) {
    return request.post<{
      user: User
      message: string
    }>('/v1/auth/register', data)
  },

  // 登出
  logout() {
    return request.post('/v1/auth/logout')
  },

  // 刷新token
  refreshToken() {
    return request.post<{
      access_token: string
      token_type: string
    }>('/v1/auth/refresh')
  },

  // 重置密码
  resetPassword(email: string) {
    return request.post('/v1/auth/reset-password', { email })
  },

  // 修改密码
  changePassword(oldPassword: string, newPassword: string) {
    return request.post('/v1/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  },
}

// 用户管理API
export const userApi = {
  // 获取当前用户信息
  getCurrentUser() {
    return request.get<User>('/v1/users/me')
  },

  // 获取用户详细档案
  getProfile() {
    return request.get<UserProfile>('/v1/users/profile')
  },

  // 更新用户档案
  updateProfile(data: Partial<UserProfile>) {
    return request.put<User>('/v1/users/profile', data)
  },

  // 上传头像
  uploadAvatar(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return request.upload<{ avatar_url: string }>('/v1/users/avatar', formData)
  },

  // 获取用户统计
  getStats() {
    return request.get<{
      total_itineraries: number
      successful_generations: number
      favorite_destinations: string[]
      recent_activities: any[]
    }>('/v1/users/stats')
  },
}

// 系统统计API
export const statsApi = {
  // 获取生成统计
  getGenerationStats() {
    return request.get<GenerationStats>('/v1/stats/generation')
  },

  // 获取热门目的地
  getPopularDestinations(limit: number = 10) {
    return request.get<Array<{
      destination: string
      count: number
      success_rate: number
    }>>('/v1/stats/popular-destinations', { params: { limit } })
  },

  // 获取系统状态
  getSystemStatus() {
    return request.get<{
      total_users: number
      total_itineraries: number
      ai_providers_status: Record<string, boolean>
      system_health: 'healthy' | 'warning' | 'error'
    }>('/v1/stats/system-status')
  },
}

// 导出所有API
export const api = {
  itinerary: itineraryApi,
  ai: aiApi,
  maps: mapsApi,
  auth: authApi,
  user: userApi,
  stats: statsApi,
} 