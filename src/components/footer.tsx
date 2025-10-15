import Link from 'next/link';
import type { FC } from 'react';

const Footer: FC = () => {
    return (
        <footer className='border-t'>
            <div className='mx-auto flex w-full max-w-7xl flex-col items-center justify-between gap-4 px-4 py-6 text-sm text-muted-foreground sm:flex-row sm:px-6 lg:px-8'>
                <p className='text-center sm:text-left'>
                    © 2025 Your Company Name. All Rights Reserved.
                </p>
                <div className='flex items-center gap-4'>
                    <Link href='#' className='hover:underline'>
                        Terms of Service
                    </Link>
                    <Link href='#' className='hover:underline'>
                        Privacy Policy
                    </Link>
                </div>
            </div>
        </footer>
    );
};

export default Footer;

