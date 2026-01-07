"use client"

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardAction } from "@/components/ui/card";
import { useState, useEffect } from "react"
import { securityCheck } from "@/lib/api/security"

export default function SecurityCard() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
      const timeout = setInterval(() => {
        handleUpdate()
      }, 2000)
  
      return () => clearInterval(timeout)
    }, [])
  
    async function handleUpdate() {
      try {
        await securityCheck()
        console.log("Polled security")
      } catch (error) {
        console.error('Error:', error)
      } finally {
      }
    }
  

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
      </Card>
    )
  }


  return (
  <Card>
    <CardHeader>
      <CardTitle>Security</CardTitle>
      <CardDescription>Security Systems</CardDescription>
    </CardHeader>
    <CardContent>

    </CardContent>
  </Card>
  );
}
