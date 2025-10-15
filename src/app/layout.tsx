import type { ReactNode } from 'react';

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

import { ThemeProvider } from 'next-themes';

import Header from '@/components/header';
import Footer from '@/components/footer';
import '@/app/globals.css';
import { Toaster } from '@/registry/new-york-v4/ui/sonner';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
    title: 'Admin Dashboard',
    description: 'A modern admin dashboard built with Next.js and shadcn/ui'
};

const Layout = ({ children }: Readonly<{ children: ReactNode }>) => {
    return (
        // Ensure dark theme default and persistent header/footer layout
        <html suppressHydrationWarning lang='en' className='dark'>
            <body
                className={`${inter.variable} bg-background text-foreground overscroll-none antialiased min-h-screen flex flex-col`}>
                <ThemeProvider attribute='class' defaultTheme='dark' enableSystem>
                    <Header />
                    <main className='flex-1'>
                        <div className='mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8'>
                            {children}
                        </div>
                    </main>
                    <Footer />
                    <Toaster />
                </ThemeProvider>
            </body>
        </html>
    );
};

export default Layout;
