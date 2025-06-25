import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, UserProfile } from '@/types'
import { api } from '@/services/api'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const profile = ref<UserProfile | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const isLoading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userName = computed(() => user.value?.full_name || user.value?.username || '用户')
  const avatar = computed(() => user.value?.avatar || '/default-avatar.png')

  // 登录
  const login = async (username: string, password: string) => {
    try {
      isLoading.value = true
      const response = await api.auth.login(username, password)
      
      token.value = response.data!.access_token
      user.value = response.data!.user
      
      // 保存token到localStorage
      localStorage.setItem('access_token', token.value)
      
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 注册
  const register = async (data: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => {
    try {
      isLoading.value = true
      const response = await api.auth.register(data)
      
      ElMessage.success(response.data!.message || '注册成功')
      return true
    } catch (error) {
      console.error('注册失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      await api.auth.logout()
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      // 清除本地状态
      user.value = null
      profile.value = null
      token.value = null
      localStorage.removeItem('access_token')
      
      ElMessage.success('已退出登录')
    }
  }

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    if (!token.value) return false

    try {
      const response = await api.user.getCurrentUser()
      user.value = response.data!
      return true
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果token无效，清除登录状态
      await logout()
      return false
    }
  }

  // 获取用户详细档案
  const fetchProfile = async () => {
    try {
      const response = await api.user.getProfile()
      profile.value = response.data!
      return true
    } catch (error) {
      console.error('获取用户档案失败:', error)
      return false
    }
  }

  // 更新用户档案
  const updateProfile = async (data: Partial<UserProfile>) => {
    try {
      isLoading.value = true
      const response = await api.user.updateProfile(data)
      
      // 更新本地用户信息
      if (user.value) {
        Object.assign(user.value, response.data!)
      }
      
      // 重新获取完整档案
      await fetchProfile()
      
      ElMessage.success('档案更新成功')
      return true
    } catch (error) {
      console.error('更新档案失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 上传头像
  const uploadAvatar = async (file: File) => {
    try {
      isLoading.value = true
      const response = await api.user.uploadAvatar(file)
      
      // 更新本地用户头像
      if (user.value) {
        user.value.avatar = response.data!.avatar_url
      }
      
      ElMessage.success('头像上传成功')
      return response.data!.avatar_url
    } catch (error) {
      console.error('头像上传失败:', error)
      return null
    } finally {
      isLoading.value = false
    }
  }

  // 修改密码
  const changePassword = async (oldPassword: string, newPassword: string) => {
    try {
      isLoading.value = true
      await api.auth.changePassword(oldPassword, newPassword)
      
      ElMessage.success('密码修改成功')
      return true
    } catch (error) {
      console.error('修改密码失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 刷新token
  const refreshToken = async () => {
    try {
      const response = await api.auth.refreshToken()
      token.value = response.data!.access_token
      localStorage.setItem('access_token', token.value)
      return true
    } catch (error) {
      console.error('刷新token失败:', error)
      await logout()
      return false
    }
  }

  // 初始化用户状态（应用启动时调用）
  const initUser = async () => {
    if (token.value) {
      await fetchCurrentUser()
    }
  }

  return {
    // 状态
    user,
    profile,
    token,
    isLoading,
    
    // 计算属性
    isLoggedIn,
    isAdmin,
    userName,
    avatar,
    
    // 方法
    login,
    register,
    logout,
    fetchCurrentUser,
    fetchProfile,
    updateProfile,
    uploadAvatar,
    changePassword,
    refreshToken,
    initUser,
  }
}) 