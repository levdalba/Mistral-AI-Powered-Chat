'use client'

/**
 * Connection status component to show backend connectivity.
 */

import { useEffect, useState } from 'react'

interface ConnectionStatusProps {
    className?: string
}

export default function ConnectionStatus({
    className = '',
}: ConnectionStatusProps) {
    const [isConnected, setIsConnected] = useState<boolean | null>(null)
    const [lastChecked, setLastChecked] = useState<Date | null>(null)

    const checkConnection = async () => {
        try {
            const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
            const response = await fetch(`${apiBaseUrl}/health`)
            const isOk = response.ok
            setIsConnected(isOk)
            setLastChecked(new Date())
        } catch (error) {
            setIsConnected(false)
            setLastChecked(new Date())
        }
    }

    useEffect(() => {
        checkConnection()
        const interval = setInterval(checkConnection, 30000) // Check every 30 seconds
        return () => clearInterval(interval)
    }, [])

    if (isConnected === null) {
        return null // Don't show anything while checking
    }

    return (
        <div className={`flex items-center space-x-2 text-sm ${className}`}>
            {isConnected ? (
                <>
                    <span className="text-green-500">📶</span>
                    <span className="text-green-600 dark:text-green-400">
                        Connected
                    </span>
                </>
            ) : (
                <>
                    <span className="text-red-500">📵</span>
                    <span className="text-red-600 dark:text-red-400">
                        Disconnected
                    </span>
                </>
            )}
            {lastChecked && (
                <span className="text-slate-500 dark:text-slate-400 text-xs">
                    {lastChecked.toLocaleTimeString()}
                </span>
            )}
        </div>
    )
}
