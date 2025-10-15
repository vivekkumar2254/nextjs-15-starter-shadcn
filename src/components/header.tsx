"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { FC } from 'react';

import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    navigationMenuTriggerStyle,
    Avatar,
    AvatarFallback,
    AvatarImage,
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
} from '@/components/ui';

const links = [
    { href: '/', label: 'Dashboard' },
    { href: '/roles', label: 'Roles' },
    { href: '/group-permission', label: 'Group Permission' }
];

const Header: FC = () => {
    const pathname = usePathname();

    return (
        <header className='sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60'>
            <div className='mx-auto flex h-14 w-full max-w-7xl items-center gap-4 px-4 sm:px-6 lg:px-8'>
                <div className='flex items-center font-semibold'>
                    <Link href='/' className='text-base sm:text-lg'>
                        Admin Panel
                    </Link>
                </div>

                <div className='flex-1' />

                <NavigationMenu className='hidden md:flex'>
                    <NavigationMenuList>
                        {links.map((link) => (
                            <NavigationMenuItem key={link.href}>
                                <NavigationMenuLink
                                    asChild
                                    className={`${navigationMenuTriggerStyle()} ${pathname === link.href ? 'bg-accent text-accent-foreground' : ''}`}
                                >
                                    <Link href={link.href}>{link.label}</Link>
                                </NavigationMenuLink>
                            </NavigationMenuItem>
                        ))}
                    </NavigationMenuList>
                </NavigationMenu>

                <div className='md:hidden'>
                    {/* Minimal mobile nav: just ensure dashboard link exists; full mobile menu can be added later */}
                    <Link href='/' className='text-sm underline'>
                        Menu
                    </Link>
                </div>

                <div className='flex flex-1 justify-end'>
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Avatar className='h-8 w-8 cursor-pointer'>
                                <AvatarImage src='' alt='User' />
                                <AvatarFallback>AD</AvatarFallback>
                            </Avatar>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align='end' className='w-48'>
                            <DropdownMenuLabel>My Account</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem asChild>
                                <Link href='#'>Profile</Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                                <Link href='#'>Settings</Link>
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem asChild>
                                <button type='button' className='w-full text-left'>Log out</button>
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </div>
        </header>
    );
};

export default Header;

