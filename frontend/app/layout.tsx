import './globals.css'

export const metadata = {
    title: 'Mistral AI Chat - Intelligent Conversations',
    description: 'Chat with Mistral AI and ask questions about your documents',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className="h-full">
            <body className="h-full antialiased">{children}</body>
        </html>
    )
}
