//
// This file would handle the API calls to your backend in a real app

import { toast } from "@/components/ui/use-toast"

const API_URL = "http://localhost:8000"

async function handleResponse(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || "An error occurred")
  }
  return response.json()
}

export async function get(endpoint: string) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        // In a real app, you would include the auth token here
        // 'Authorization': `Bearer ${getToken()}`
      },
      credentials: "include",
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("API get error:", error)
    toast({
      title: "Error",
      description: error instanceof Error ? error.message : "Failed to fetch data",
      variant: "destructive",
    })
    throw error
  }
}

export async function post(endpoint: string, data: any) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // In a real app, you would include the auth token here
        // 'Authorization': `Bearer ${getToken()}`
      },
      credentials: "include",
      body: JSON.stringify(data),
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("API post error:", error)
    toast({
      title: "Error",
      description: error instanceof Error ? error.message : "Failed to submit data",
      variant: "destructive",
    })
    throw error
  }
}

export async function put(endpoint: string, data: any) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        // In a real app, you would include the auth token here
        // 'Authorization': `Bearer ${getToken()}`
      },
      credentials: "include",
      body: JSON.stringify(data),
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("API put error:", error)
    toast({
      title: "Error",
      description: error instanceof Error ? error.message : "Failed to update data",
      variant: "destructive",
    })
    throw error
  }
}

export async function del(endpoint: string) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        // In a real app, you would include the auth token here
        // 'Authorization': `Bearer ${getToken()}`
      },
      credentials: "include",
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("API delete error:", error)
    toast({
      title: "Error",
      description: error instanceof Error ? error.message : "Failed to delete data",
      variant: "destructive",
    })
    throw error
  }
}

export async function postFormData(endpoint: string, formData: FormData) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: {
        // No Content-Type header for FormData
        // In a real app, you would include the auth token here
        // 'Authorization': `Bearer ${getToken()}`
      },
      credentials: "include",
      body: formData,
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("API postFormData error:", error)
    toast({
      title: "Error",
      description: error instanceof Error ? error.message : "Failed to upload data",
      variant: "destructive",
    })
    throw error
  }
}
