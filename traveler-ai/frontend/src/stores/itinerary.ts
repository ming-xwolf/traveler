import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Itinerary,
  ItineraryGenerationRequest,
  DailyItinerary,
  GenerationProgress,
  AIProvider,
  Template
} from '@/types'
import { api } from '@/services/api'
import { ElMessage } from 'element-plus'

export const useItineraryStore = defineStore('itinerary', () => {
  // 状态
  const itineraries = ref<Itinerary[]>([])
  const currentItinerary = ref<Itinerary | null>(null)
  const dailyItineraries = ref<DailyItinerary[]>([])
  const generationProgress = ref<GenerationProgress | null>(null)
  const aiProviders = ref<AIProvider[]>([])
  const templates = ref<Template[]>([])
  const isLoading = ref(false)
  const isGenerating = ref(false)

  // 计算属性
  const completedItineraries = computed(() => 
    itineraries.value.filter(item => item.status === 'completed')
  )
  
  const pendingItineraries = computed(() => 
    itineraries.value.filter(item => item.status === 'pending' || item.status === 'generating')
  )

  const availableProviders = computed(() => 
    aiProviders.value.filter(provider => provider.status === 'available')
  )

  const currentProgress = computed(() => 
    generationProgress.value?.progress || 0
  )

  // 生成攻略
  const generateItinerary = async (request: ItineraryGenerationRequest) => {
    try {
      isGenerating.value = true
      const response = await api.itinerary.generate(request)
      
      const newItinerary = response.data!
      itineraries.value.unshift(newItinerary)
      currentItinerary.value = newItinerary
      
      // 开始轮询生成进度
      startProgressPolling(newItinerary.id)
      
      ElMessage.success('开始生成攻略...')
      return newItinerary
    } catch (error) {
      console.error('生成攻略失败:', error)
      ElMessage.error('生成攻略失败')
      return null
    } finally {
      isGenerating.value = false
    }
  }

  // 轮询生成进度
  const startProgressPolling = (itineraryId: number) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await api.itinerary.getProgress(itineraryId)
        generationProgress.value = response.data!
        
        // 更新攻略状态
        const index = itineraries.value.findIndex(item => item.id === itineraryId)
        if (index !== -1) {
          itineraries.value[index].status = response.data!.status as any
          itineraries.value[index].progress = response.data!.progress
        }

        // 生成完成或失败时停止轮询
        if (response.data!.status === 'completed' || response.data!.status === 'failed') {
          clearInterval(pollInterval)
          
          if (response.data!.status === 'completed') {
            ElMessage.success('攻略生成完成！')
            // 获取完整的攻略数据
            await fetchItineraryDetail(itineraryId)
          } else {
            ElMessage.error('攻略生成失败')
          }
        }
      } catch (error) {
        console.error('获取生成进度失败:', error)
        clearInterval(pollInterval)
      }
    }, 2000) // 每2秒查询一次
  }

  // 获取攻略详情
  const fetchItineraryDetail = async (itineraryId: number) => {
    try {
      isLoading.value = true
      const response = await api.itinerary.getDetail(itineraryId)
      
      currentItinerary.value = response.data!.itinerary
      dailyItineraries.value = response.data!.daily_itineraries
      
      // 更新列表中的攻略
      const index = itineraries.value.findIndex(item => item.id === itineraryId)
      if (index !== -1) {
        itineraries.value[index] = response.data!.itinerary
      }
      
      return response.data!
    } catch (error) {
      console.error('获取攻略详情失败:', error)
      return null
    } finally {
      isLoading.value = false
    }
  }

  // 获取攻略列表
  const fetchItineraries = async (params?: {
    page?: number
    page_size?: number
    status?: string
    destination?: string
  }) => {
    try {
      isLoading.value = true
      const response = await api.itinerary.getList(params)
      
      itineraries.value = response.data!.data.items
      return response.data!
    } catch (error) {
      console.error('获取攻略列表失败:', error)
      return null
    } finally {
      isLoading.value = false
    }
  }

  // 删除攻略
  const deleteItinerary = async (itineraryId: number) => {
    try {
      await api.itinerary.delete(itineraryId)
      
      // 从列表中移除
      const index = itineraries.value.findIndex(item => item.id === itineraryId)
      if (index !== -1) {
        itineraries.value.splice(index, 1)
      }
      
      // 如果删除的是当前攻略，清除当前状态
      if (currentItinerary.value?.id === itineraryId) {
        currentItinerary.value = null
        dailyItineraries.value = []
      }
      
      ElMessage.success('攻略删除成功')
      return true
    } catch (error) {
      console.error('删除攻略失败:', error)
      return false
    }
  }

  // 导出攻略
  const exportItinerary = async (itineraryId: number, format: 'markdown' | 'html' | 'pdf') => {
    try {
      const blob = await api.itinerary.export(itineraryId, format)
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // 设置文件名
      const itinerary = itineraries.value.find(item => item.id === itineraryId)
      const fileName = `${itinerary?.title || '旅游攻略'}.${format}`
      link.download = fileName
      
      // 触发下载
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      ElMessage.success(`${format.toUpperCase()} 文件下载成功`)
      return true
    } catch (error) {
      console.error('导出攻略失败:', error)
      return false
    }
  }

  // 验证目的地
  const validateDestination = async (destination: string) => {
    try {
      const response = await api.itinerary.validateDestination(destination)
      return response.data!
    } catch (error) {
      console.error('验证目的地失败:', error)
      return { valid: false, suggestions: [] }
    }
  }

  // 获取AI服务商列表
  const fetchAIProviders = async () => {
    try {
      const response = await api.ai.getProviders()
      aiProviders.value = response.data!
      return response.data!
    } catch (error) {
      console.error('获取AI服务商失败:', error)
      return []
    }
  }

  // 测试AI连接
  const testAIConnection = async (provider: string) => {
    try {
      const response = await api.ai.testConnection(provider)
      
      if (response.data!.status === 'success') {
        ElMessage.success(`${provider} 连接正常`)
      } else {
        ElMessage.warning(`${provider} 连接异常: ${response.data!.message}`)
      }
      
      return response.data!
    } catch (error) {
      console.error('测试AI连接失败:', error)
      ElMessage.error(`${provider} 连接测试失败`)
      return { status: 'failed', message: '连接测试失败' }
    }
  }

  // 获取模板列表
  const fetchTemplates = async (type?: 'overview' | 'daily') => {
    try {
      const response = await api.itinerary.getTemplates(type)
      templates.value = response.data!
      return response.data!
    } catch (error) {
      console.error('获取模板列表失败:', error)
      return []
    }
  }

  // 获取示例攻略
  const fetchExamples = async () => {
    try {
      const response = await api.itinerary.getExamples()
      return response.data!
    } catch (error) {
      console.error('获取示例攻略失败:', error)
      return null
    }
  }

  // 清除当前攻略
  const clearCurrentItinerary = () => {
    currentItinerary.value = null
    dailyItineraries.value = []
    generationProgress.value = null
  }

  // 设置当前攻略
  const setCurrentItinerary = (itinerary: Itinerary) => {
    currentItinerary.value = itinerary
    // 如果需要获取详细信息
    if (itinerary.status === 'completed') {
      fetchItineraryDetail(itinerary.id)
    }
  }

  return {
    // 状态
    itineraries,
    currentItinerary,
    dailyItineraries,
    generationProgress,
    aiProviders,
    templates,
    isLoading,
    isGenerating,
    
    // 计算属性
    completedItineraries,
    pendingItineraries,
    availableProviders,
    currentProgress,
    
    // 方法
    generateItinerary,
    fetchItineraryDetail,
    fetchItineraries,
    deleteItinerary,
    exportItinerary,
    validateDestination,
    fetchAIProviders,
    testAIConnection,
    fetchTemplates,
    fetchExamples,
    clearCurrentItinerary,
    setCurrentItinerary,
  }
}) 