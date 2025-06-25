import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import { ApiResponse } from '@/types'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 60000, // 增加超时时间，特别是AI生成可能需要较长时间
  headers: {
    'Content-Type': 'application/json',
  },
})

// 加载实例
let loadingInstance: any = null

// 显示加载
const showLoading = (text = '正在处理中...') => {
  loadingInstance = ElLoading.service({
    lock: true,
    text,
    background: 'rgba(0, 0, 0, 0.7)',
  })
}

// 隐藏加载
const hideLoading = () => {
  if (loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

// 请求拦截器
service.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 添加认证token
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 对于长时间操作显示loading
    if (config.url?.includes('/generate') || config.url?.includes('/upload')) {
      showLoading(config.url.includes('/generate') ? '正在生成攻略...' : '正在处理中...')
    }

    return config
  },
  (error) => {
    hideLoading()
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    hideLoading()
    
    const { data } = response
    
    // 检查响应数据格式
    if (typeof data !== 'object') {
      ElMessage.error('响应数据格式错误')
      return Promise.reject(new Error('响应数据格式错误'))
    }

    // 检查业务状态码
    if (data.success === false) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }

    return response
  },
  (error) => {
    hideLoading()
    
    console.error('Response error:', error)
    
    // 网络错误
    if (!error.response) {
      ElMessage.error('网络连接失败，请检查网络设置')
      return Promise.reject(error)
    }

    const { status, data } = error.response

    // 根据状态码处理不同错误
    switch (status) {
      case 401:
        ElMessage.error('认证失败，请重新登录')
        // 清除token并跳转到登录页
        localStorage.removeItem('access_token')
        window.location.href = '/login'
        break
      case 403:
        ElMessage.error('权限不足')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 422:
        // 表单验证错误
        if (data?.detail && Array.isArray(data.detail)) {
          const errorMsg = data.detail.map((item: any) => item.msg).join(', ')
          ElMessage.error(`参数错误: ${errorMsg}`)
        } else {
          ElMessage.error(data?.message || '参数验证失败')
        }
        break
      case 429:
        ElMessage.error('请求过于频繁，请稍后再试')
        break
      case 500:
        ElMessage.error('服务器内部错误')
        break
      default:
        ElMessage.error(data?.message || `请求失败 (${status})`)
    }

    return Promise.reject(error)
  }
)

// 通用请求方法
export const request = {
  // GET请求
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.get(url, config).then(res => res.data)
  },

  // POST请求
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.post(url, data, config).then(res => res.data)
  },

  // PUT请求
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.put(url, data, config).then(res => res.data)
  },

  // DELETE请求
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.delete(url, config).then(res => res.data)
  },

  // PATCH请求
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.patch(url, data, config).then(res => res.data)
  },

  // 上传文件
  upload<T = any>(url: string, formData: FormData, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.post(url, formData, {
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data',
      },
    }).then(res => res.data)
  },

  // 下载文件
  download(url: string, config?: AxiosRequestConfig): Promise<Blob> {
    return service.get(url, {
      ...config,
      responseType: 'blob',
    }).then(res => res.data)
  },
}

export default service 