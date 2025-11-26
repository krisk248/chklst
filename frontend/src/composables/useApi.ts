import axios, { AxiosInstance, AxiosError } from 'axios'
import { ref } from 'vue'

interface ApiResponse<T = any> {
  data: T
  status: number
  statusText: string
}

const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export function useApi() {
  const error = ref<AxiosError | null>(null)
  const isLoading = ref(false)

  const request = async <T = any>(
    method: string,
    url: string,
    data?: any,
    config?: any
  ): Promise<ApiResponse<T>> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient({
        method,
        url,
        data,
        ...config,
      })
      return {
        data: response.data,
        status: response.status,
        statusText: response.statusText,
      }
    } catch (err) {
      error.value = err as AxiosError
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const get = <T = any>(url: string, config?: any): Promise<ApiResponse<T>> => {
    return request<T>('GET', url, undefined, config)
  }

  const post = <T = any>(
    url: string,
    data?: any,
    config?: any
  ): Promise<ApiResponse<T>> => {
    return request<T>('POST', url, data, config)
  }

  const put = <T = any>(
    url: string,
    data?: any,
    config?: any
  ): Promise<ApiResponse<T>> => {
    return request<T>('PUT', url, data, config)
  }

  const patch = <T = any>(
    url: string,
    data?: any,
    config?: any
  ): Promise<ApiResponse<T>> => {
    return request<T>('PATCH', url, data, config)
  }

  const del = <T = any>(url: string, config?: any): Promise<ApiResponse<T>> => {
    return request<T>('DELETE', url, undefined, config)
  }

  return {
    error,
    isLoading,
    request,
    get,
    post,
    put,
    patch,
    delete: del,
  }
}

export function useWebSocket(url: string, onMessage?: (data: any) => void) {
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)

  const connect = () => {
    try {
      socket.value = new WebSocket(url)

      socket.value.onopen = () => {
        isConnected.value = true
        console.log('WebSocket connected')
      }

      socket.value.onmessage = (event) => {
        if (onMessage) {
          onMessage(JSON.parse(event.data))
        }
      }

      socket.value.onerror = (error) => {
        console.error('WebSocket error:', error)
        isConnected.value = false
      }

      socket.value.onclose = () => {
        isConnected.value = false
        console.log('WebSocket disconnected')
      }
    } catch (err) {
      console.error('Failed to connect WebSocket:', err)
    }
  }

  const send = (data: any) => {
    if (socket.value && isConnected.value) {
      socket.value.send(JSON.stringify(data))
    }
  }

  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
    }
  }

  return {
    socket,
    isConnected,
    connect,
    send,
    disconnect,
  }
}
