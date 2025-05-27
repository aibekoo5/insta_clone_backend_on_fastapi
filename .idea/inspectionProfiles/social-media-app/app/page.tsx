import { redirect } from "next/navigation"
import HomePage from "@/components/home/home-page"
import { cookies } from "next/headers"


export default async function Home() {
  // Check for the access_token cookie (or whatever your auth cookie is named)

  const cookieStore = await cookies()
  const accessToken = cookieStore.get("access_token")

  if (!accessToken) {
    redirect("/login")
  }

  return <HomePage />
}