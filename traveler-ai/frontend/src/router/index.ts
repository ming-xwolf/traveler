import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: '首页',
      description: 'TravelerAI - 智能旅游攻略生成平台'
    }
  },
  {
    path: '/generate',
    name: 'Generate',
    component: () => import('@/views/Generate.vue'),
    meta: {
      title: '生成攻略',
      description: '使用AI生成个性化旅游攻略',
      requiresAuth: false // 游客可以体验
    }
  },
  {
    path: '/itinerary/:id',
    name: 'ItineraryDetail',
    component: () => import('@/views/ItineraryDetail.vue'),
    meta: {
      title: '攻略详情',
      description: '查看详细的旅游攻略内容'
    }
  },
  {
    path: '/my-itineraries',
    name: 'MyItineraries',
    component: () => import('@/views/MyItineraries.vue'),
    meta: {
      title: '我的攻略',
      description: '管理我的旅游攻略',
      requiresAuth: true
    }
  },
  {
    path: '/templates',
    name: 'Templates',
    component: () => import('@/views/Templates.vue'),
    meta: {
      title: '攻略模板',
      description: '浏览和管理攻略模板'
    }
  },
  {
    path: '/examples',
    name: 'Examples',
    component: () => import('@/views/Examples.vue'),
    meta: {
      title: '示例攻略',
      description: '参考精选的示例攻略'
    }
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/views/Auth.vue'),
    meta: {
      title: '登录注册',
      description: '用户认证页面',
      hideForLoggedIn: true
    },
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/components/auth/LoginForm.vue'),
        meta: {
          title: '登录'
        }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/components/auth/RegisterForm.vue'),
        meta: {
          title: '注册'
        }
      }
    ]
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: {
      title: '个人中心',
      description: '管理个人账户和偏好设置',
      requiresAuth: true
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      title: '控制台',
      description: '系统管理控制台',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: {
      title: '关于我们',
      description: '了解TravelerAI平台'
    }
  },
  {
    path: '/help',
    name: 'Help',
    component: () => import('@/views/Help.vue'),
    meta: {
      title: '帮助中心',
      description: '使用指南和常见问题'
    }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/404.vue'),
    meta: {
      title: '页面未找到',
      description: '抱歉，您访问的页面不存在'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 如果有保存的位置（例如使用浏览器后退按钮）
    if (savedPosition) {
      return savedPosition
    }
    // 如果有锚点
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    }
    // 默认滚动到顶部
    return { top: 0, behavior: 'smooth' }
  }
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - TravelerAI`
  }

  // 检查认证要求
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 检查管理员权限
    if (to.meta.requiresAdmin && !userStore.isAdmin) {
      ElMessage.error('权限不足')
      next({ name: 'Home' })
      return
    }
  }

  // 如果用户已登录，重定向某些页面
  if (to.meta.hideForLoggedIn && userStore.isLoggedIn) {
    next({ name: 'Home' })
    return
  }

  // 初始化用户状态
  if (userStore.token && !userStore.user) {
    try {
      await userStore.fetchCurrentUser()
    } catch (error) {
      console.error('初始化用户状态失败:', error)
    }
  }

  next()
})

// 全局后置钩子
router.afterEach((to, from) => {
  // 可以在这里添加页面访问统计等逻辑
  console.log(`导航到: ${to.name} (${to.path})`)
})

// 错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  ElMessage.error('页面加载失败，请重试')
})

export default router 