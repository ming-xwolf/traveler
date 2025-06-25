<template>
  <el-container class="app-layout">
    <!-- 顶部导航栏 -->
    <el-header class="app-header" height="60px">
      <div class="header-content">
        <!-- Logo和标题 -->
        <div class="logo-section">
          <router-link to="/" class="logo-link">
            <el-icon size="32" color="#409EFF">
              <Location />
            </el-icon>
            <span class="logo-text">TravelerAI</span>
          </router-link>
        </div>

        <!-- 导航菜单 -->
        <el-menu
          :default-active="$route.name"
          mode="horizontal"
          class="header-menu"
          router
        >
          <el-menu-item index="Home">首页</el-menu-item>
          <el-menu-item index="Generate">生成攻略</el-menu-item>
          <el-menu-item index="Templates">攻略模板</el-menu-item>
          <el-menu-item index="Examples">示例攻略</el-menu-item>
          <el-sub-menu index="help" v-if="!isMobile">
            <template #title>帮助</template>
            <el-menu-item index="Help">使用指南</el-menu-item>
            <el-menu-item index="About">关于我们</el-menu-item>
          </el-sub-menu>
        </el-menu>

        <!-- 用户操作区 -->
        <div class="user-actions">
          <template v-if="userStore.isLoggedIn">
            <!-- 我的攻略 -->
            <el-button
              type="text"
              @click="$router.push('/my-itineraries')"
              class="action-button"
            >
              <el-icon><Document /></el-icon>
              <span v-if="!isMobile">我的攻略</span>
            </el-button>

            <!-- 用户菜单 -->
            <el-dropdown @command="handleUserCommand">
              <span class="user-dropdown">
                <el-avatar :size="32" :src="userStore.avatar">
                  {{ userStore.userName.charAt(0) }}
                </el-avatar>
                <span v-if="!isMobile" class="username">{{ userStore.userName }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="dashboard" v-if="userStore.isAdmin">
                    <el-icon><Setting /></el-icon>
                    管理控制台
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <template v-else>
            <el-button
              type="primary"
              @click="$router.push('/auth/login')"
              size="small"
            >
              登录
            </el-button>
            <el-button
              @click="$router.push('/auth/register')"
              size="small"
              v-if="!isMobile"
            >
              注册
            </el-button>
          </template>

          <!-- 移动端菜单按钮 -->
          <el-button
            v-if="isMobile"
            type="text"
            @click="drawerVisible = true"
            class="mobile-menu-button"
          >
            <el-icon size="20"><Menu /></el-icon>
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主内容区域 -->
    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <!-- 底部 -->
    <el-footer class="app-footer" height="auto">
      <div class="footer-content">
        <div class="footer-section">
          <h4>TravelerAI</h4>
          <p>智能旅游攻略生成平台</p>
          <p>让AI帮您规划完美旅行</p>
        </div>
        <div class="footer-section">
          <h4>功能特色</h4>
          <ul>
            <li>智能攻略生成</li>
            <li>个性化推荐</li>
            <li>多格式导出</li>
            <li>实时地理信息</li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>技术支持</h4>
          <ul>
            <li>多AI模型支持</li>
            <li>百度地图API</li>
            <li>实时天气信息</li>
            <li>路线规划</li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>联系我们</h4>
          <p>邮箱: support@travelerai.com</p>
          <p>QQ群: 123456789</p>
          <div class="social-links">
            <el-link href="#" type="primary">GitHub</el-link>
            <el-link href="#" type="primary">微博</el-link>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2024 TravelerAI. All rights reserved.</p>
      </div>
    </el-footer>

    <!-- 移动端抽屉菜单 -->
    <el-drawer
      v-model="drawerVisible"
      title="菜单"
      direction="rtl"
      size="280px"
    >
      <el-menu
        :default-active="$route.name"
        router
        @select="drawerVisible = false"
      >
        <el-menu-item index="Home">
          <el-icon><House /></el-icon>
          首页
        </el-menu-item>
        <el-menu-item index="Generate">
          <el-icon><Magic /></el-icon>
          生成攻略
        </el-menu-item>
        <el-menu-item index="Templates">
          <el-icon><Document /></el-icon>
          攻略模板
        </el-menu-item>
        <el-menu-item index="Examples">
          <el-icon><Star /></el-icon>
          示例攻略
        </el-menu-item>
        <el-menu-item index="Help">
          <el-icon><QuestionFilled /></el-icon>
          使用指南
        </el-menu-item>
        <el-menu-item index="About">
          <el-icon><InfoFilled /></el-icon>
          关于我们
        </el-menu-item>
      </el-menu>
    </el-drawer>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  Location,
  Document,
  User,
  Setting,
  SwitchButton,
  ArrowDown,
  Menu,
  House,
  Magic,
  Star,
  QuestionFilled,
  InfoFilled
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const drawerVisible = ref(false)
const windowWidth = ref(window.innerWidth)

// 计算属性
const isMobile = computed(() => windowWidth.value < 768)

// 窗口大小变化监听
const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (!isMobile.value) {
    drawerVisible.value = false
  }
}

// 用户下拉菜单命令处理
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'dashboard':
      router.push('/dashboard')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '确认退出',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        await userStore.logout()
        router.push('/')
      } catch (error) {
        // 用户取消操作
      }
      break
  }
}

// 生命周期
onMounted(() => {
  window.addEventListener('resize', handleResize)
  // 初始化用户状态
  userStore.initUser()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.app-layout {
  min-height: 100vh;
  background: var(--el-bg-color-page);
}

.app-header {
  background: #fff;
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 0;
  
  .header-content {
    height: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .logo-section {
    .logo-link {
      display: flex;
      align-items: center;
      text-decoration: none;
      color: var(--el-text-color-primary);
      
      .logo-text {
        margin-left: 8px;
        font-size: 20px;
        font-weight: 600;
        color: #409EFF;
      }
    }
  }

  .header-menu {
    flex: 1;
    max-width: 600px;
    margin: 0 32px;
    border-bottom: none;

    @media (max-width: 768px) {
      display: none;
    }
  }

  .user-actions {
    display: flex;
    align-items: center;
    gap: 16px;

    .action-button {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 8px 12px;
    }

    .user-dropdown {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      
      .username {
        max-width: 100px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .mobile-menu-button {
      padding: 8px;
    }
  }
}

.app-main {
  min-height: calc(100vh - 200px);
  padding: 0;
}

.app-footer {
  background: #f8f9fa;
  border-top: 1px solid var(--el-border-color-light);
  padding: 32px 0 16px;

  .footer-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 16px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 32px;

    .footer-section {
      h4 {
        color: var(--el-text-color-primary);
        margin-bottom: 16px;
        font-size: 16px;
        font-weight: 600;
      }

      p {
        color: var(--el-text-color-regular);
        margin-bottom: 8px;
        line-height: 1.5;
      }

      ul {
        list-style: none;
        padding: 0;
        margin: 0;

        li {
          color: var(--el-text-color-regular);
          margin-bottom: 8px;
          line-height: 1.5;
        }
      }

      .social-links {
        display: flex;
        gap: 16px;
        margin-top: 12px;
      }
    }
  }

  .footer-bottom {
    max-width: 1200px;
    margin: 24px auto 0;
    padding: 16px;
    border-top: 1px solid var(--el-border-color-lighter);
    text-align: center;
    color: var(--el-text-color-regular);
    font-size: 14px;
  }
}

// 页面过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 响应式适配
@media (max-width: 768px) {
  .app-header .header-content {
    padding: 0 12px;
  }

  .app-footer .footer-content {
    padding: 0 12px;
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style> 